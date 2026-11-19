"""Teste le modèle de base sur des phrases libres.
Usage : python scripts/tester_baseline.py "phrase 1" "phrase 2" ..."""
import csv, sys
import numpy as np
from sklearn.pipeline import make_pipeline, make_union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
ORDRE = ["Anti-Aura", "Aura Correcte", "Forte Aura", "Aura Divine"]
C = [(-100, -11), (-10, 24), (25, 74), (75, 100)]
def cls(s): s = int(round(max(-100, min(100, s)))); return next(i for i, (a, b) in enumerate(C) if a <= s <= b)
def feats(): return make_union(TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                               TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True))
tr = list(csv.DictReader(open("data/train_synthetique.csv", encoding="utf-8-sig"))) + list(csv.DictReader(open("data/grok_textes.csv", encoding="utf-8-sig")))
X = [r["texte"] for r in tr]
clf = make_pipeline(feats(), LogisticRegression(max_iter=3000, C=4, class_weight="balanced")).fit(X, [ORDRE.index(r["classe"]) for r in tr])
reg = make_pipeline(feats(), Ridge(alpha=1.0)).fit(X, [float(r["score"]) for r in tr])
for t in sys.argv[1:]:
    pr = clf.predict_proba([t])[0]; k = int(pr.argmax()); s = float(reg.predict([t])[0])
    print(f"{t}\n   classification : {ORDRE[k]} (confiance {pr[k]:.0%}) | " + " ".join(f"{o.replace("Aura ", "").replace(" Aura", "")}={v:.0%}" for o, v in zip(ORDRE, pr)) +
          f"\n   régression     : score {s:+.0f} -> {ORDRE[cls(s)]}\n")
