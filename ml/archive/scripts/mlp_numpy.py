"""Perceptron multicouche écrit à la main en NumPy (aucun pré-entraînement).

Entrée TF-IDF (mots 1-2 + caractères 2-5, ajusté sur le train uniquement) -> Dense(h1) -> Dense(h2) -> Dense(4) + softmax.
Propagation avant / rétropropagation codées à la main, init He (ReLU) ou Xavier (tanh), entropie croisée
pondérée par classe, mini-batches, Adam codé à la main, dropout inversé, early stopping sur la validation.

  python scripts/mlp_numpy.py                    # gradient check + entraînement avec la config par défaut
  python scripts/mlp_numpy.py --recherche        # 8 essais d'hyperparamètres (choix sur la validation uniquement)
"""
import argparse, itertools, json, os, sys, time

import joblib
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_union

sys.path.insert(0, os.path.dirname(__file__))
from commun import (TRAIN_DEFAUT, TEST_DEFAUT, ORDRE, charger, classes, poids_classes, metriques,
                    afficher_matrice, courbes, sauver_resultats)

DOSSIER = "models/mlp_numpy"


# ---------------------------------------------------------------- réseau
class MLP:
    def __init__(self, n_in, h1=128, h2=64, n_out=4, act="relu", dropout=0.3, seed=42):
        self.act, self.dropout = act, dropout
        self.rng = np.random.default_rng(seed)
        tailles = [n_in, h1, h2, n_out]
        self.p = {}
        for i, (a, b) in enumerate(zip(tailles[:-1], tailles[1:]), 1):
            if act == "relu" and i < 3:
                std = np.sqrt(2.0 / a)                       # He
                self.p[f"W{i}"] = self.rng.normal(0, std, (a, b))
            else:
                lim = np.sqrt(6.0 / (a + b))                 # Xavier / Glorot uniforme
                self.p[f"W{i}"] = self.rng.uniform(-lim, lim, (a, b))
            self.p[f"b{i}"] = np.zeros(b)

    def n_parametres(self): return int(sum(v.size for v in self.p.values()))

    def _f(self, z): return np.maximum(z, 0) if self.act == "relu" else np.tanh(z)
    def _df(self, z, a): return (z > 0).astype(z.dtype) if self.act == "relu" else 1 - a ** 2

    def forward(self, X, train=False):
        p, c = self.p, {"X": X}
        c["Z1"] = X @ p["W1"] + p["b1"]; c["A1"] = self._f(c["Z1"])
        if train and self.dropout > 0:
            c["M1"] = (self.rng.random(c["A1"].shape) > self.dropout) / (1 - self.dropout); c["A1"] = c["A1"] * c["M1"]
        c["Z2"] = c["A1"] @ p["W2"] + p["b2"]; c["A2"] = self._f(c["Z2"])
        if train and self.dropout > 0:
            c["M2"] = (self.rng.random(c["A2"].shape) > self.dropout) / (1 - self.dropout); c["A2"] = c["A2"] * c["M2"]
        Z3 = c["A2"] @ p["W3"] + p["b3"]
        Z3 = Z3 - Z3.max(1, keepdims=True)                  # stabilité numérique
        E = np.exp(Z3); c["P"] = E / E.sum(1, keepdims=True)  # softmax
        return c

    @staticmethod
    def perte(P, y, w):
        """Entropie croisée pondérée : sum_i w_{y_i} * -log p_i[y_i] / sum_i w_{y_i}."""
        wi = w[y]
        return float(np.sum(wi * -np.log(P[np.arange(len(y)), y] + 1e-12)) / wi.sum())

    def backward(self, c, y, w):
        p, g = self.p, {}
        wi = w[y]; n = wi.sum()
        dZ3 = c["P"].copy(); dZ3[np.arange(len(y)), y] -= 1; dZ3 *= (wi / n)[:, None]   # dL/dZ3 (softmax + CE)
        g["W3"] = c["A2"].T @ dZ3; g["b3"] = dZ3.sum(0)
        dA2 = dZ3 @ p["W3"].T
        if "M2" in c: dA2 = dA2 * c["M2"]
        A2 = self._f(c["Z2"])                                # activation avant dropout
        dZ2 = dA2 * self._df(c["Z2"], A2)
        g["W2"] = c["A1"].T @ dZ2; g["b2"] = dZ2.sum(0)
        dA1 = dZ2 @ p["W2"].T
        if "M1" in c: dA1 = dA1 * c["M1"]
        A1 = self._f(c["Z1"])
        dZ1 = dA1 * self._df(c["Z1"], A1)
        g["W1"] = np.asarray(c["X"].T @ dZ1); g["b1"] = dZ1.sum(0)
        return g

    def predict_proba(self, X, batch=1024):
        return np.vstack([self.forward(X[i:i + batch])["P"] for i in range(0, X.shape[0], batch)])


class Adam:
    def __init__(self, params, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8, l2=0.0):
        self.lr, self.b1, self.b2, self.eps, self.l2, self.t = lr, b1, b2, eps, l2, 0
        self.m = {k: np.zeros_like(v) for k, v in params.items()}
        self.v = {k: np.zeros_like(v) for k, v in params.items()}

    def step(self, params, grads):
        self.t += 1
        for k in params:
            g = grads[k] + (self.l2 * params[k] if k.startswith("W") else 0)
            self.m[k] = self.b1 * self.m[k] + (1 - self.b1) * g
            self.v[k] = self.b2 * self.v[k] + (1 - self.b2) * g ** 2
            mh = self.m[k] / (1 - self.b1 ** self.t)          # correction de biais
            vh = self.v[k] / (1 - self.b2 ** self.t)
            params[k] -= self.lr * mh / (np.sqrt(vh) + self.eps)


# ---------------------------------------------------------------- gradient check
def gradient_check(X, y, w, act="relu", n_verif=15, eps=1e-5, seed=0):
    """Compare le gradient analytique aux différences finies centrées sur un petit lot (dropout coupé)."""
    net = MLP(X.shape[1], 16, 8, 4, act=act, dropout=0.0, seed=seed)
    g = net.backward(net.forward(X), y, w)
    rng = np.random.default_rng(seed); pire = 0.0
    for k, W in net.p.items():
        if k == "W1":   # on vérifie en priorité les poids reliés à des features non nulles du lot
            lignes = np.unique(X.nonzero()[1])
            idx = [(rng.choice(lignes), rng.integers(W.shape[1])) for _ in range(n_verif)]
        else:
            idx = [tuple(rng.integers(s) for s in W.shape) for _ in range(n_verif)]
        erreurs, ignores = [], 0
        signes = lambda c: (np.sign(c["Z1"]), np.sign(c["Z2"]))
        for i in idx:
            old = W[i]
            W[i] = old + eps; cp = net.forward(X); lp = MLP.perte(cp["P"], y, w)
            W[i] = old - eps; cm = net.forward(X); lm = MLP.perte(cm["P"], y, w)
            W[i] = old
            if act == "relu" and any((a != b).any() for a, b in zip(signes(cp), signes(cm))):
                ignores += 1; continue   # la perturbation traverse le point anguleux de ReLU (non dérivable en 0)
            num = (lp - lm) / (2 * eps); ana = g[k][i]
            erreurs.append(abs(num - ana) / max(1e-8, abs(num) + abs(ana)))
        e = max(erreurs) if erreurs else 0.0; pire = max(pire, e)
        print(f"  gradient check {k:3s} : erreur relative max = {e:.2e}" + (f"  ({ignores} coord. ignorée(s) : point anguleux ReLU)" if ignores else ""))
    ok = pire < 1e-5
    print(f"  => {'OK' if ok else 'ÉCHEC'} (seuil 1e-5)")
    return ok


# ---------------------------------------------------------------- entraînement
def entrainer(Xtr, ytr, Xva, yva, w, h1=128, h2=64, act="relu", dropout=0.3, lr=1e-3, l2=1e-5,
              batch=64, epochs=60, patience=5, seed=42, verbose=True):
    net = MLP(Xtr.shape[1], h1, h2, 4, act, dropout, seed)
    opt = Adam(net.p, lr=lr, l2=l2)
    rng = np.random.default_rng(seed)
    hist = {"train": [], "val": []}; best = (np.inf, None, 0); attente = 0
    for ep in range(1, epochs + 1):
        perm = rng.permutation(Xtr.shape[0]); pertes = []
        for i in range(0, len(perm), batch):
            b = perm[i:i + batch]
            c = net.forward(Xtr[b], train=True)
            pertes.append(MLP.perte(c["P"], ytr[b], w) * len(b))
            opt.step(net.p, net.backward(c, ytr[b], w))
        lt = sum(pertes) / len(perm)
        lv = MLP.perte(net.predict_proba(Xva), yva, w)
        hist["train"].append(lt); hist["val"].append(lv)
        if verbose: print(f"  epoch {ep:2d}  loss train={lt:.4f}  val={lv:.4f}")
        if lv < best[0] - 1e-4:
            best = (lv, {k: v.copy() for k, v in net.p.items()}, ep); attente = 0
        else:
            attente += 1
            if attente >= patience:
                if verbose: print(f"  early stopping (pas d'amélioration depuis {patience} epochs)")
                break
    net.p = best[1]
    return net, hist, best[2]


def vectoriseur(max_features=20000):
    return make_union(
        TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True, max_features=max_features // 4),
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True, max_features=max_features * 3 // 4))


def charger_modele(dossier=DOSSIER):
    cfg = json.load(open(os.path.join(dossier, "config.json"), encoding="utf-8"))
    net = MLP(cfg["n_in"], cfg["h1"], cfg["h2"], 4, cfg["act"], 0.0)
    net.p = dict(np.load(os.path.join(dossier, "poids.npz")))
    vec = joblib.load(os.path.join(dossier, "vectoriseur.joblib"))
    return lambda textes: net.predict_proba(vec.transform(textes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="+", default=TRAIN_DEFAUT)
    ap.add_argument("--test", default=TEST_DEFAUT)
    ap.add_argument("--recherche", action="store_true", help="petite recherche d'hyperparamètres sur la validation")
    ap.add_argument("--h1", type=int, default=128); ap.add_argument("--h2", type=int, default=64)
    ap.add_argument("--act", choices=["relu", "tanh"], default="relu")
    ap.add_argument("--dropout", type=float, default=0.3); ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--max-features", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    np.random.seed(a.seed)

    tr, va, test = charger(a.train, a.test, seed=a.seed)
    print(f"Train {len(tr)} | validation {len(va)} (tirée du train) | test réel {len(test)}")
    vec = vectoriseur(a.max_features)
    Xtr = sparse.csr_matrix(vec.fit_transform([r["texte"] for r in tr]), dtype=np.float64)   # ajusté sur le train seul
    Xva = sparse.csr_matrix(vec.transform([r["texte"] for r in va]), dtype=np.float64)
    ytr, yva = classes(tr), classes(va)
    w = poids_classes(ytr)
    print(f"TF-IDF : {Xtr.shape[1]} features | poids de classes : {np.round(w, 3).tolist()}")

    print("\nGradient check (8 exemples, réseau 16-8, dropout coupé) :")
    for act in ("relu", "tanh"):
        print(f" activation {act}");
        if not gradient_check(Xtr[:8], ytr[:8], w, act=act): sys.exit("Gradient check échoué : on n'entraîne pas.")

    if a.recherche:
        grille = [dict(lr=lr, h1=h1, h2=h1 // 2, dropout=d) for lr, h1, d in itertools.product([1e-3, 3e-4], [128, 256], [0.3, 0.5])]
    else:
        grille = [dict(lr=a.lr, h1=a.h1, h2=a.h2, dropout=a.dropout)]
    essais = []
    for k, cfg in enumerate(grille, 1):
        print(f"\nEssai {k}/{len(grille)} : {cfg}")
        t0 = time.time()
        net, hist, best_ep = entrainer(Xtr, ytr, Xva, yva, w, act=a.act, seed=a.seed, **cfg)
        duree = time.time() - t0
        pv = net.predict_proba(Xva).argmax(1); m = metriques(yva, pv)
        essais.append(dict(cfg=cfg, val_loss=min(hist["val"]), best_epoch=best_ep, epochs=len(hist["train"]),
                           temps_s=duree, **{f"val_{k2}": v for k2, v in m.items()}, _net=net, _hist=hist))
        print(f"  -> val loss={min(hist['val']):.4f} kappa={m['kappa_quadratique']:.3f} F1={m['f1_macro']:.3f} ({duree:.0f} s)")

    meilleur = min(essais, key=lambda e: e["val_loss"])   # choix sur la VALIDATION uniquement
    os.makedirs("results", exist_ok=True)
    if a.recherche:
        with open("results/mlp_numpy_recherche.md", "w", encoding="utf-8") as f:
            f.write("| # | lr | h1-h2 | dropout | epochs (meilleure) | val loss | val kappa | val F1 | temps (s) |\n|---|---|---|---|---|---|---|---|---|\n")
            for k, e in enumerate(essais, 1):
                c = e["cfg"]; mark = " **←**" if e is meilleur else ""
                f.write(f"| {k}{mark} | {c['lr']:g} | {c['h1']}-{c['h2']} | {c['dropout']} | {e['epochs']} ({e['best_epoch']}) | "
                        f"{e['val_loss']:.4f} | {e['val_kappa_quadratique']:.3f} | {e['val_f1_macro']:.3f} | {e['temps_s']:.0f} |\n")
        print(open("results/mlp_numpy_recherche.md", encoding="utf-8").read())

    net, hist = meilleur["_net"], meilleur["_hist"]
    courbes(hist, "results/courbes_mlp_numpy.png", f"MLP NumPy {meilleur['cfg']}", meilleur["best_epoch"])
    os.makedirs(DOSSIER, exist_ok=True)
    np.savez(os.path.join(DOSSIER, "poids.npz"), **net.p)
    joblib.dump(vec, os.path.join(DOSSIER, "vectoriseur.joblib"))
    json.dump(dict(n_in=Xtr.shape[1], act=a.act, **meilleur["cfg"]), open(os.path.join(DOSSIER, "config.json"), "w"))

    res = {"config": meilleur["cfg"], "activation": a.act, "best_epoch": meilleur["best_epoch"],
           "temps_entrainement_s": meilleur["temps_s"], "n_parametres": net.n_parametres(),
           "historique": hist, "validation_synthetique": {k: v for k, v in meilleur.items() if k.startswith("val_")}}
    if test:   # évaluation unique sur le test réel, APRÈS le choix du modèle
        Xte = vec.transform([r["texte"] for r in test]); yte = classes(test)
        pte = net.predict_proba(Xte).argmax(1)
        res["test_reel"] = metriques(yte, pte)
        print("\nTest réel :", {k: round(v, 3) for k, v in res["test_reel"].items()})
        afficher_matrice(yte, pte)
        sauver_resultats("mlp_numpy", res, test, pte)
    print(f"\nModèle sauvegardé dans {DOSSIER}/ — {net.n_parametres():,} paramètres, {meilleur['temps_s']:.0f} s d'entraînement")


if __name__ == "__main__":
    main()
