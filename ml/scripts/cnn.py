"""CNN pour textes (architecture de Kim, 2014), entraîné de zéro : aucun embedding ni tokenizer pré-entraîné.

texte -> mots -> numéros -> Embedding (appris) -> convolutions 1D de plusieurs largeurs (2, 3, 4… mots)
      -> ReLU -> max-pooling sur toute la phrase -> concaténation -> dropout -> couche linéaire -> 4 classes

Chaque filtre de largeur k agit comme un détecteur de « motif de k mots » (ex. « c'est vous ! ») ;
le max-pooling garde, pour chaque filtre, l'endroit du texte où le motif est le plus présent.
"""
import collections, json, os, re, time

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import cohen_kappa_score


def tokeniser(t):
    """Minuscules ; sépare les élisions (« l'aura » -> « l' » + « aura ») ; garde ponctuation et emojis."""
    return re.findall(r"[^\W_]+['’](?=[^\W_])|[^\W_]+|[^\w\s]", str(t).lower())


def construire_vocab(textes, min_freq=2):
    """Vocabulaire construit sur le TRAIN uniquement. 0 = remplissage, 1 = mot inconnu."""
    compte = collections.Counter(m for t in textes for m in tokeniser(t))
    return {m: i + 2 for i, m in enumerate(sorted(m for m, c in compte.items() if c >= min_freq))}


def encoder(textes, vocab, longueur_max, longueur_min=5):
    ids = [[vocab.get(m, 1) for m in tokeniser(t)][:longueur_max] or [1] for t in textes]
    L = max(longueur_min, max(map(len, ids)))           # au moins la largeur du plus grand filtre
    X = torch.zeros(len(ids), L, dtype=torch.long)
    for i, s in enumerate(ids): X[i, :len(s)] = torch.tensor(s)
    return X


class TextCNN(nn.Module):
    def __init__(self, n_mots, embedding=128, n_filtres=100, largeurs=(2, 3, 4), dropout=0.5, n_classes=4):
        super().__init__()
        self.emb = nn.Embedding(n_mots, embedding, padding_idx=0)
        self.convs = nn.ModuleList([nn.Conv1d(embedding, n_filtres, k) for k in largeurs])
        self.drop = nn.Dropout(dropout)
        self.sortie = nn.Linear(n_filtres * len(largeurs), n_classes)

    def forward(self, x):
        e = self.emb(x).transpose(1, 2)                                   # (batch, embedding, mots)
        h = [torch.relu(conv(e)).max(dim=2).values for conv in self.convs]  # max-pooling global par filtre
        return self.sortie(self.drop(torch.cat(h, dim=1)))


def entrainer(train_textes, train_y, val_textes, val_y, cfg, device="cpu", graine=42, verbose=False):
    """Entraîne un CNN avec la configuration cfg ; early stopping sur le kappa quadratique de la validation."""
    torch.manual_seed(graine); np.random.seed(graine)
    vocab = construire_vocab(train_textes, cfg.get("min_freq", 2))
    Xtr, Xva = encoder(train_textes, vocab, cfg["longueur_max"]), encoder(val_textes, vocab, cfg["longueur_max"])
    ytr = torch.tensor(np.asarray(train_y)); yva = np.asarray(val_y)
    poids = torch.tensor(len(ytr) / (4 * np.bincount(np.asarray(train_y), minlength=4)), dtype=torch.float, device=device)
    modele = TextCNN(len(vocab) + 2, cfg["embedding"], cfg["n_filtres"], tuple(cfg["largeurs"]), cfg["dropout"]).to(device)
    opt = torch.optim.Adam(modele.parameters(), lr=cfg["lr"], weight_decay=cfg.get("weight_decay", 0))
    critere = nn.CrossEntropyLoss(weight=poids)
    hist = {"train": [], "val_kappa": []}; meilleur = (-1, None, 0); attente = 0; t0 = time.time()
    for epoch in range(1, cfg["epochs_max"] + 1):
        modele.train(); total = 0
        for i in torch.randperm(len(ytr)).split(cfg["batch"]):
            opt.zero_grad(); l = critere(modele(Xtr[i].to(device)), ytr[i].to(device)); l.backward(); opt.step()
            total += l.item() * len(i)
        k = cohen_kappa_score(yva, predire_classes(modele, Xva, device), weights="quadratic")
        hist["train"].append(total / len(ytr)); hist["val_kappa"].append(k)
        if verbose: print(f"epoch {epoch} : perte train {total / len(ytr):.3f} | kappa validation {k:.3f}")
        if k > meilleur[0] + 1e-4: meilleur, attente = (k, {a: b.detach().clone() for a, b in modele.state_dict().items()}, epoch), 0
        else:
            attente += 1
            if attente >= cfg["patience"]: break
    modele.load_state_dict(meilleur[1]); modele.eval()
    return dict(modele=modele, vocab=vocab, cfg=cfg, hist=hist, best_epoch=meilleur[2], val_kappa=meilleur[0],
                temps_s=time.time() - t0, n_parametres=sum(p.numel() for p in modele.parameters()))


@torch.no_grad()
def predire_proba(modele, X, device="cpu", lot=256):
    modele.eval()
    return torch.cat([modele(X[i:i + lot].to(device)).softmax(1).cpu() for i in range(0, len(X), lot)]).numpy()


def predire_classes(modele, X, device="cpu"): return predire_proba(modele, X, device).argmax(1)


def sauver(res, dossier):
    os.makedirs(dossier, exist_ok=True)
    torch.save(res["modele"].state_dict(), os.path.join(dossier, "modele.pt"))
    json.dump(dict(cfg=res["cfg"], vocab=res["vocab"], val_kappa=res["val_kappa"], best_epoch=res["best_epoch"]),
              open(os.path.join(dossier, "config.json"), "w", encoding="utf-8"), ensure_ascii=False)


def charger(dossier, device="cpu"):
    """Retourne une fonction textes -> probabilités (4 classes)."""
    c = json.load(open(os.path.join(dossier, "config.json"), encoding="utf-8")); cfg, vocab = c["cfg"], c["vocab"]
    m = TextCNN(len(vocab) + 2, cfg["embedding"], cfg["n_filtres"], tuple(cfg["largeurs"]), cfg["dropout"])
    m.load_state_dict(torch.load(os.path.join(dossier, "modele.pt"), map_location=device)); m.to(device).eval()
    return lambda textes: predire_proba(m, encoder(textes, vocab, cfg["longueur_max"]), device)
