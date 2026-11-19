"""Prédire l'aura de nouveaux textes avec l'un des 3 modèles du projet.

  python scripts/predire.py "Le chaos, c'est vous !"                  # CamemBERT (modèle retenu, ensemble)
  python scripts/predire.py --modele svm "Loin des yeux, loin du cœur"
  python scripts/predire.py --modele cnn --fichier mes_textes.txt     # un texte par ligne

Les modèles SVM et CNN sont créés par notebook_aura.ipynb (models/svm.joblib, models/cnn/) ;
l'ensemble CamemBERT par scripts/train_camembert_v2.py + scripts/phase2_final.py (results/p2_choix.json).
"""
import argparse, json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from commun import ORDRE

CENTRES = np.array([-55.0, 7.0, 50.0, 87.0])   # score moyen de chaque classe

ap = argparse.ArgumentParser()
ap.add_argument("textes", nargs="*")
ap.add_argument("--fichier")
ap.add_argument("--modele", choices=["camembert", "svm", "cnn"], default="camembert")
a = ap.parse_args()
textes = list(a.textes) + ([l.strip() for l in open(a.fichier, encoding="utf-8") if l.strip()] if a.fichier else [])
if not textes: ap.error("donne au moins un texte ou --fichier")

if a.modele == "svm":
    import joblib
    proba = joblib.load("models/svm.joblib").predict_proba(textes)
    for t, p in zip(textes, proba): print(f"{ORDRE[p.argmax()]:16s} probabilité={p.max():.0%} | {t[:80]}")
elif a.modele == "cnn":
    import cnn
    proba = cnn.charger("models/cnn")(textes)
    for t, p in zip(textes, proba): print(f"{ORDRE[p.argmax()]:16s} probabilité={p.max():.0%} | {t[:80]}")
else:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    choix = json.load(open("results/p2_choix.json", encoding="utf-8")); retenu = choix["candidats"][choix["meilleur"]]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    score = 0
    for nom, w in retenu["composants"].items():
        if nom == "tfidf": continue
        d = f"models/{nom}/final"
        tok = AutoTokenizer.from_pretrained(d); m = AutoModelForSequenceClassification.from_pretrained(d).to(device).eval()
        with torch.no_grad():
            o = m(**tok(textes, truncation=True, max_length=256, padding=True, return_tensors="pt").to(device)).logits.cpu()
        score = score + w * ((o.reshape(-1) * 100).numpy() if o.shape[-1] == 1 else o.softmax(-1).numpy() @ CENTRES)
    for t, s in zip(textes, score):
        print(f"{ORDRE[int(np.digitize(s, retenu['seuils']))]:16s} score≈{s:+4.0f} | {t[:80]}")
print(f"(modèle : {a.modele})")
