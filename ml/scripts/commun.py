"""Fonctions partagées par les modèles entraînés de zéro (mlp_numpy.py, train_from_scratch.py)."""
import csv, json, os

import numpy as np
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split

ORDRE = ["Anti-Aura", "Aura Correcte", "Forte Aura", "Aura Divine"]
SEUILS = [(-100, -11), (-10, 24), (25, 74), (75, 100)]
COURT = ["Anti", "Corr", "Fort", "Divi"]
TRAIN_DEFAUT = ["data/train_synthetique.csv", "data/grok_textes.csv", "data/paires_contrastees.csv"]
TEST_DEFAUT = "data/test_reel.csv"


def score_vers_classe(s):
    s = int(round(max(-100, min(100, s))))
    return next(i for i, (a, b) in enumerate(SEUILS) if a <= s <= b)


def lire(chemins):
    rows = []
    for p in chemins:
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            if r.get("texte", "").strip() and r.get("classe", "").strip() in ORDRE:
                r["_fichier"] = os.path.basename(p)
                rows.append(r)
    return rows


def charger(train_paths, test_path, mode="classification", val_frac=0.1, seed=42, keep_v1_scores=False):
    """Train/validation (tirée du train, stratifiée) et test réel. Le test n'intervient jamais dans l'apprentissage."""
    train = lire(train_paths)
    if mode == "regression":
        train = [r for r in train if r.get("score", "").strip() != ""]
        if not keep_v1_scores:
            train = [r for r in train if r.get("origine") != "v1_poesie"]  # ancienne formule de score
    test = lire([test_path]) if test_path and os.path.exists(test_path) else []
    test_txt = {r["texte"] for r in test}
    train = [r for r in train if r["texte"] not in test_txt]
    y = [ORDRE.index(r["classe"]) for r in train]
    tr, va = train_test_split(train, test_size=val_frac, stratify=y, random_state=seed)
    return tr, va, test


def classes(rows): return np.array([ORDRE.index(r["classe"]) for r in rows])
def scores(rows): return np.array([float(r["score"]) for r in rows])


def poids_classes(y):
    cnt = np.bincount(y, minlength=4)
    return len(y) / (4 * np.maximum(cnt, 1))


def metriques(y, p):
    y, p = np.asarray(y), np.asarray(p)
    return dict(accuracy=float(accuracy_score(y, p)), a_une_classe_pres=float(np.mean(np.abs(y - p) <= 1)),
                f1_macro=float(f1_score(y, p, average="macro", labels=list(range(4)), zero_division=0)),
                kappa_quadratique=float(cohen_kappa_score(y, p, weights="quadratic", labels=list(range(4)))))


def afficher_matrice(y, p):
    print("      " + " ".join(f"{c:>5}" for c in COURT))
    for c, row in zip(COURT, confusion_matrix(y, p, labels=list(range(4)))):
        print(f"{c:>5} " + " ".join(f"{v:>5}" for v in row))


def courbes(hist, chemin, titre, best_epoch=None):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    ep = range(1, len(hist["train"]) + 1)
    ax.plot(ep, hist["train"], label="train")
    ax.plot(ep, hist["val"], label="validation")
    if best_epoch: ax.axvline(best_epoch, ls="--", c="gray", label=f"meilleur ({best_epoch})")
    ax.set_xlabel("epoch"); ax.set_ylabel("loss"); ax.set_title(titre); ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(chemin, dpi=120); plt.close(fig)


def sauver_resultats(nom, res, test, pred):
    os.makedirs("results", exist_ok=True)
    json.dump(res, open(f"results/{nom}.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False, default=float)
    with open(f"results/predictions_{nom}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["id", "texte", "classe_reference", "prediction"])
        for r, k in zip(test, pred): w.writerow([r.get("id", ""), r["texte"], r["classe"], ORDRE[k]])
