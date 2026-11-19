"""Modèle de base Aura : TF-IDF (mots + caractères) + régression logistique.
Entraîné sur les données synthétiques (v1 + v3), évalué (a) en validation croisée
sur le synthétique et (b) sur le jeu de test réel."""
import argparse, csv, json, os, sys, time
import numpy as np
from sklearn.pipeline import make_pipeline, make_union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, confusion_matrix
ORDRE = ["Anti-Aura", "Aura Correcte", "Forte Aura", "Aura Divine"]
C = [(-100, -11), (-10, 24), (25, 74), (75, 100)]
def cls(s): s = round(s); return next(i for i, (a, b) in enumerate(C) if a <= max(-100, min(100, s)) <= b)
def lire(p): return list(csv.DictReader(open(p, encoding="utf-8-sig")))

ap = argparse.ArgumentParser()
ap.add_argument("test", nargs="?", default="data/test_reel.csv")
ap.add_argument("--train", nargs="+", default=["data/train_synthetique.csv"])
ap.add_argument("--nom", default="baseline", help="préfixe des fichiers de sortie dans results/")
ap.add_argument("--no-cv", action="store_true", help="sauter la validation croisée")
a = ap.parse_args()
train = [r for p in a.train for r in lire(p) if r.get("texte", "").strip() and r.get("classe") in ORDRE]
test = lire(a.test)
print("Train :", len(train), "textes", a.train)
Xtr = [r["texte"] for r in train]; ytr = np.array([ORDRE.index(r["classe"]) for r in train]); str_ = np.array([float(r["score"]) for r in train])
Xte = [r["texte"] for r in test]; yte = np.array([ORDRE.index(r["classe"]) for r in test])

def feats():
    return make_union(TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                      TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True))
clf = make_pipeline(feats(), LogisticRegression(max_iter=3000, C=4, class_weight="balanced"))
reg = make_pipeline(feats(), Ridge(alpha=1.0))

RES = {}
def rapport(nom, y, p):
    RES[nom] = dict(accuracy=accuracy_score(y, p), a_une_classe_pres=float(np.mean(abs(y - p) <= 1)),
                    f1_macro=f1_score(y, p, average='macro', labels=range(4), zero_division=0),
                    kappa_quadratique=cohen_kappa_score(y, p, weights='quadratic', labels=list(range(4))))
    print(f"{nom:38s} acc={accuracy_score(y, p):.1%}  ±1={np.mean(abs(y - p) <= 1):.1%}  "
          f"F1-macro={f1_score(y, p, average='macro', labels=range(4), zero_division=0):.2f}  "
          f"kappa-q={cohen_kappa_score(y, p, weights='quadratic', labels=list(range(4))):.2f}")

cv = StratifiedKFold(5, shuffle=True, random_state=0)
if not a.no_cv: rapport("Synthétique, validation croisée (clf)", ytr, cross_val_predict(clf, Xtr, ytr, cv=cv))
t0 = time.time(); clf.fit(Xtr, ytr); t_clf = time.time() - t0; pc = clf.predict(Xte)
t0 = time.time(); reg.fit(Xtr, str_); t_reg = time.time() - t0; pr = np.array([cls(s) for s in reg.predict(Xte)])
rapport("Test réel — classification", yte, pc)
rapport("Test réel — régression du score", yte, pr)
rapport("Test réel — toujours 'Aura Correcte'", yte, np.full_like(yte, 1))

print("\nMatrice test réel, classification (lignes = vérité)")
m = confusion_matrix(yte, pc, labels=range(4)); ab = ["Anti", "Corr", "Fort", "Divi"]
print("      " + " ".join(f"{c:>5}" for c in ab))
for c, row in zip(ab, m): print(f"{c:>5} " + " ".join(f"{v:>5}" for v in row))
print("\nPrédictions par type de texte (classification) :")
for t in sorted({r["type"] for r in test}):
    idx = [i for i, r in enumerate(test) if r["type"] == t]
    print(f"  {t:15s} n={len(idx):3d}  acc={np.mean(pc[idx] == yte[idx]):.0%}  classes prédites = "
          + ", ".join(f"{ab[k]}:{v}" for k, v in zip(*np.unique(pc[idx], return_counts=True))))
os.makedirs("results", exist_ok=True)
RES["temps_entrainement_s"] = {"classification": t_clf, "regression": t_reg}
RES["n_parametres"] = {"classification": int(clf[-1].coef_.size + clf[-1].intercept_.size), "regression": int(reg[-1].coef_.size + 1)}
json.dump(RES, open(f"results/{a.nom}.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False, default=float)
with open(f"results/predictions_{a.nom}.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["id", "texte", "classe_reference", "prediction_classif", "prediction_regression"])
    for r, a, b in zip(test, pc, pr): w.writerow([r["id"], r["texte"], r["classe"], ORDRE[a], ORDRE[b]])
