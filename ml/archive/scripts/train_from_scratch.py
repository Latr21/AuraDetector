"""BiLSTM PyTorch entraîné de zéro (aucun poids, embedding ni tokenizer pré-entraîné).

Tokenisation maison (minuscules, regex mots / ponctuation / emojis), vocabulaire construit sur le train uniquement
(fréquence >= 2, <PAD>=0, <UNK>=1). Embedding(128, aléatoire) -> BiLSTM -> pooling max + moyenne (masqué)
-> Dense + dropout -> sortie (4 logits ou 1 score). Adam, gradient clipping, early stopping sur la validation.

  python scripts/train_from_scratch.py                         # classification
  python scripts/train_from_scratch.py --mode regression       # prédit le score, convertit avec les seuils officiels
  python scripts/train_from_scratch.py --recherche             # 8 essais d'hyperparamètres (validation uniquement)
"""
import argparse, collections, itertools, json, os, random, re, sys, time

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(__file__))
from commun import (TRAIN_DEFAUT, TEST_DEFAUT, ORDRE, charger, classes, scores, poids_classes, metriques,
                    afficher_matrice, courbes, sauver_resultats, score_vers_classe)

# élisions (l', qu', t'…), mots (lettres/chiffres), emojis / pictogrammes, puis toute autre ponctuation
TOKEN_RE = re.compile(r"[^\W_]+['’](?=[^\W_])|[^\W_]+|[\U0001F000-\U0001FAFF☀-➿]|[^\w\s]", re.UNICODE)


def tokeniser(t): return TOKEN_RE.findall(t.lower())


class Vocab:
    def __init__(self, textes=None, min_freq=2, itos=None):
        if itos is None:
            cnt = collections.Counter(tok for t in textes for tok in tokeniser(t))
            itos = ["<PAD>", "<UNK>"] + sorted(w for w, c in cnt.items() if c >= min_freq)
        self.itos = itos; self.stoi = {w: i for i, w in enumerate(itos)}

    def __len__(self): return len(self.itos)
    def encoder(self, t, max_len): return [self.stoi.get(w, 1) for w in tokeniser(t)][:max_len] or [1]


def lots(ids, y, batch, shuffle, rng=None):
    ordre = np.arange(len(ids))
    if shuffle: rng.shuffle(ordre)
    for i in range(0, len(ordre), batch):
        b = ordre[i:i + batch]; L = max(len(ids[j]) for j in b)
        x = torch.zeros(len(b), L, dtype=torch.long)
        for k, j in enumerate(b): x[k, :len(ids[j])] = torch.tensor(ids[j])
        yield x, torch.as_tensor(y[b])


class BiLSTM(nn.Module):
    def __init__(self, n_vocab, emb=128, hidden=128, couches=1, dropout=0.3, n_out=4):
        super().__init__()
        self.emb = nn.Embedding(n_vocab, emb, padding_idx=0)            # initialisé au hasard
        self.lstm = nn.LSTM(emb, hidden, num_layers=couches, batch_first=True, bidirectional=True,
                            dropout=dropout if couches > 1 else 0.0)
        self.drop = nn.Dropout(dropout)
        self.dense = nn.Linear(4 * hidden, hidden)                        # [max ; moyenne] x 2 directions
        self.out = nn.Linear(hidden, n_out)

    def forward(self, x):
        mask = (x != 0).unsqueeze(-1).float()
        h, _ = self.lstm(self.drop(self.emb(x)))
        h_max = h.masked_fill(mask == 0, -1e9).max(1).values
        h_moy = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
        z = torch.relu(self.dense(self.drop(torch.cat([h_max, h_moy], -1))))
        return self.out(self.drop(z))


def entrainer(Xtr, ytr, Xva, yva, n_vocab, mode, w, lr=1e-3, hidden=128, couches=1, dropout=0.3, emb=128,
              batch=64, epochs=30, patience=4, clip=1.0, seed=42, device="cpu", verbose=True):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    reg = mode == "regression"
    net = BiLSTM(n_vocab, emb, hidden, couches, dropout, 1 if reg else 4).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    crit = nn.MSELoss() if reg else nn.CrossEntropyLoss(weight=torch.tensor(w, dtype=torch.float, device=device))

    def perte_lot(x, y):
        o = net(x.to(device)); y = y.to(device)
        return crit(o.squeeze(-1), y.float()) if reg else crit(o, y.long())

    hist = {"train": [], "val": []}; best = (np.inf, None, 0); attente = 0
    for ep in range(1, epochs + 1):
        net.train(); tot = 0.0
        for x, y in lots(Xtr, ytr, batch, True, rng):
            opt.zero_grad(); l = perte_lot(x, y); l.backward()
            nn.utils.clip_grad_norm_(net.parameters(), clip)                # gradient clipping
            opt.step(); tot += l.item() * len(y)
        net.eval(); vt = 0.0
        with torch.no_grad():
            for x, y in lots(Xva, yva, 256, False): vt += perte_lot(x, y).item() * len(y)
        lt, lv = tot / len(ytr), vt / len(yva)
        hist["train"].append(lt); hist["val"].append(lv)
        if verbose: print(f"  epoch {ep:2d}  loss train={lt:.4f}  val={lv:.4f}")
        if lv < best[0] - 1e-4:
            best = (lv, {k: v.detach().cpu().clone() for k, v in net.state_dict().items()}, ep); attente = 0
        else:
            attente += 1
            if attente >= patience:
                if verbose: print(f"  early stopping à l'epoch {ep} (meilleure : {best[2]})")
                break
    net.load_state_dict(best[1])
    return net, hist, best[2]


@torch.no_grad()
def predire_ids(net, ids, mode, device="cpu"):
    net.eval(); out = []
    for x, _ in lots(ids, np.zeros(len(ids)), 256, False): out.append(net(x.to(device)).cpu())
    o = torch.cat(out)
    if mode == "regression": return o.squeeze(-1).numpy() * 100
    return o.softmax(-1).numpy()


def en_classes(sortie, mode):
    return np.array([score_vers_classe(s) for s in sortie]) if mode == "regression" else sortie.argmax(1)


def charger_modele(dossier):
    cfg = json.load(open(os.path.join(dossier, "config.json"), encoding="utf-8"))
    vocab = Vocab(itos=cfg["itos"])
    net = BiLSTM(len(vocab), cfg["emb"], cfg["hidden"], cfg["couches"], cfg["dropout"], 1 if cfg["mode"] == "regression" else 4)
    net.load_state_dict(torch.load(os.path.join(dossier, "modele.pt"), map_location="cpu"))
    return lambda textes: predire_ids(net, [vocab.encoder(t, cfg["max_len"]) for t in textes], cfg["mode"]), cfg["mode"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="+", default=TRAIN_DEFAUT)
    ap.add_argument("--test", default=TEST_DEFAUT)
    ap.add_argument("--mode", choices=["classification", "regression"], default="classification")
    ap.add_argument("--recherche", action="store_true")
    ap.add_argument("--lr", type=float, default=1e-3); ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--couches", type=int, default=1); ap.add_argument("--dropout", type=float, default=0.3)
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--device", default="cpu", help="cpu (par défaut) ou cuda")
    ap.add_argument("--threads", type=int, default=0, help="threads CPU PyTorch (0 = défaut)")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    if a.threads: torch.set_num_threads(a.threads)
    nom = "bilstm_" + ("regression" if a.mode == "regression" else "classif")

    tr, va, test = charger(a.train, a.test, mode=a.mode, seed=a.seed)
    vocab = Vocab([r["texte"] for r in tr], min_freq=2)                  # train uniquement (pas la validation)
    enc = lambda rows: [vocab.encoder(r["texte"], a.max_len) for r in rows]
    Xtr, Xva = enc(tr), enc(va)
    if a.mode == "regression": ytr, yva = scores(tr) / 100, scores(va) / 100
    else: ytr, yva = classes(tr), classes(va)
    w = poids_classes(classes(tr))
    print(f"[{a.mode}] train {len(tr)} | validation {len(va)} | test {len(test)} | vocabulaire {len(vocab)} | device {a.device}")

    if a.recherche:
        grille = [dict(lr=lr, hidden=h, dropout=d) for lr, h, d in itertools.product([1e-3, 3e-3], [64, 128], [0.3, 0.5])]
    else:
        grille = [dict(lr=a.lr, hidden=a.hidden, dropout=a.dropout)]
    essais = []
    for k, cfg in enumerate(grille, 1):
        print(f"\nEssai {k}/{len(grille)} : {cfg}")
        t0 = time.time()
        net, hist, best_ep = entrainer(Xtr, ytr, Xva, yva, len(vocab), a.mode, w, couches=a.couches,
                                       seed=a.seed, device=a.device, **cfg)
        duree = time.time() - t0
        yv_cls = classes(va); pv = en_classes(predire_ids(net, Xva, a.mode, a.device), a.mode)
        m = metriques(yv_cls, pv)
        essais.append(dict(cfg=cfg, val_loss=min(hist["val"]), best_epoch=best_ep, epochs=len(hist["train"]), temps_s=duree,
                           **{f"val_{k2}": v for k2, v in m.items()}, _net=net, _hist=hist))
        print(f"  -> val loss={min(hist['val']):.4f} kappa={m['kappa_quadratique']:.3f} F1={m['f1_macro']:.3f} ({duree:.0f} s)")

    meilleur = min(essais, key=lambda e: e["val_loss"])                  # choix sur la validation uniquement
    os.makedirs("results", exist_ok=True)
    if a.recherche:
        with open(f"results/{nom}_recherche.md", "w", encoding="utf-8") as f:
            f.write("| # | lr | hidden | dropout | epochs (meilleure) | val loss | val kappa | val F1 | temps (s) |\n|---|---|---|---|---|---|---|---|---|\n")
            for k, e in enumerate(essais, 1):
                c = e["cfg"]; mark = " **←**" if e is meilleur else ""
                f.write(f"| {k}{mark} | {c['lr']:g} | {c['hidden']} | {c['dropout']} | {e['epochs']} ({e['best_epoch']}) | "
                        f"{e['val_loss']:.4f} | {e['val_kappa_quadratique']:.3f} | {e['val_f1_macro']:.3f} | {e['temps_s']:.0f} |\n")
        print(open(f"results/{nom}_recherche.md", encoding="utf-8").read())

    net, hist = meilleur["_net"], meilleur["_hist"]
    courbes(hist, f"results/courbes_{nom}.png", f"BiLSTM {a.mode} {meilleur['cfg']}", meilleur["best_epoch"])
    dossier = f"models/{nom}"; os.makedirs(dossier, exist_ok=True)
    torch.save({k: v.cpu() for k, v in net.state_dict().items()}, os.path.join(dossier, "modele.pt"))
    json.dump(dict(mode=a.mode, emb=128, couches=a.couches, max_len=a.max_len, itos=vocab.itos, **meilleur["cfg"]),
              open(os.path.join(dossier, "config.json"), "w", encoding="utf-8"), ensure_ascii=False)

    n_par = sum(p.numel() for p in net.parameters())
    res = {"mode": a.mode, "config": meilleur["cfg"], "couches": a.couches, "best_epoch": meilleur["best_epoch"],
           "temps_entrainement_s": meilleur["temps_s"], "device": a.device, "n_parametres": n_par, "vocabulaire": len(vocab),
           "historique": hist, "validation_synthetique": {k: v for k, v in meilleur.items() if k.startswith("val_")}}
    if test:
        net = net.to(a.device)
        pte = en_classes(predire_ids(net, enc(test), a.mode, a.device), a.mode); yte = classes(test)
        res["test_reel"] = metriques(yte, pte)
        print("\nTest réel :", {k: round(v, 3) for k, v in res["test_reel"].items()})
        afficher_matrice(yte, pte)
        sauver_resultats(nom, res, test, pte)
    print(f"\nModèle sauvegardé dans {dossier}/ — {n_par:,} paramètres, {meilleur['temps_s']:.0f} s d'entraînement")


if __name__ == "__main__":
    main()
