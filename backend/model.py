"""Registre des 3 modèles Aura servis par l'API : CamemBERT (modèle retenu), SVM et CNN.

Les modèles sont lus dans ml/models/ :
  - CamemBERT : ensemble choisi en phase 2 (ml/results/p2_choix.json + ml/models/p2_*/final)
  - SVM       : ml/models/svm.joblib   (créé par ml/notebook_aura.ipynb)
  - CNN       : ml/models/cnn/         (créé par ml/notebook_aura.ipynb)
Chargement à la demande puis mise en cache. CPU par défaut ; AURA_DEVICE=cuda pour le GPU.

Chaque modèle renvoie : catégorie, probabilité, probabilités des 4 classes et un score d'aura (-100..100).
Pour CamemBERT (score continu), les « probabilités » sont une distribution douce autour du score prédit ;
pour le SVM et le CNN, le score est l'espérance Σ p_k · centre_k.
"""
import hashlib
import json
import os
import sys
import threading
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ML = ROOT / "ml"
MODELS = ML / "models"
sys.path.insert(0, str(ML / "scripts"))

ORDRE = ["Anti-Aura", "Aura Correcte", "Forte Aura", "Aura Divine"]
CENTRES = np.array([-55.0, 7.0, 50.0, 87.0])
DEVICE = os.environ.get("AURA_DEVICE", "cpu")


def proba_depuis_score(s, temperature=18.0):
    z = -np.abs(s - CENTRES) / temperature
    p = np.exp(z - z.max())
    return p / p.sum()


# ------------------------------------------------------------------ modèles
class CamembertEnsemble:
    """Moyenne pondérée des scores de plusieurs CamemBERT + seuils choisis sur la validation."""
    def __init__(self, retenu):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        self.torch, self.seuils, self.parts = torch, tuple(retenu["seuils"]), []
        for nom, w in retenu["composants"].items():
            if nom == "tfidf" or w <= 0: continue
            d = MODELS / nom / "final"
            self.parts.append((w, AutoTokenizer.from_pretrained(d), AutoModelForSequenceClassification.from_pretrained(d).to(DEVICE).eval()))
        tot = sum(w for w, _, _ in self.parts); self.parts = [(w / tot, t, m) for w, t, m in self.parts]

    def predire(self, text):
        s = 0.0
        with self.torch.no_grad():
            for w, tok, m in self.parts:
                o = m(**tok([text], truncation=True, max_length=256, return_tensors="pt").to(DEVICE)).logits[0].cpu().numpy()
                if o.size == 1: s += w * float(o[0]) * 100
                else: e = np.exp(o - o.max()); s += w * float((e / e.sum()) @ CENTRES)
        return int(np.digitize(s, self.seuils)), proba_depuis_score(s), s


class SvmModel:
    def __init__(self):
        import joblib
        self.pipe = joblib.load(MODELS / "svm.joblib")

    def predire(self, text):
        p = self.pipe.predict_proba([text])[0]; return int(p.argmax()), p, float(p @ CENTRES)


class CnnModel:
    def __init__(self):
        import cnn
        self.f = cnn.charger(str(MODELS / "cnn"), DEVICE)

    def predire(self, text):
        p = self.f([text])[0]; return int(p.argmax()), p, float(p @ CENTRES)


class DemoModel:
    def predire(self, text):
        s = hashlib.sha256(text.encode()).digest()[0] / 255 * 200 - 100
        p = proba_depuis_score(s); return int(p.argmax()), p, s


# ------------------------------------------------------------------ registre
def _kappas():
    """Kappa test de chaque modèle, écrit par le notebook (results/comparaison_3_modeles.json)."""
    f = ML / "results" / "comparaison_3_modeles.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def decouvrir():
    k = _kappas()
    desc = lambda base, cle: base + (f" — kappa test {k[cle]:.3f}".replace(".", ",") if cle in k else "")
    reg = []
    choix_f = ML / "results" / "p2_choix.json"
    if choix_f.exists():
        choix = json.loads(choix_f.read_text(encoding="utf-8")); retenu = choix["candidats"][choix["meilleur"]]
        if all((MODELS / n / "final").exists() for n, w in retenu["composants"].items() if n != "tfidf" and w > 0):
            reg.append(dict(id="camembert", label="⭐ CamemBERT (modèle retenu)", famille="pré-entraîné",
                            description=desc("Pré-entraîné sur le français, ensemble large + base", "camembert"),
                            loader=lambda r=retenu: CamembertEnsemble(r)))
    if (MODELS / "svm.joblib").exists():
        reg.append(dict(id="svm", label="SVM", famille="machine learning",
                        description=desc("TF-IDF + SVM linéaire, ultra rapide", "svm"), loader=SvmModel))
    if (MODELS / "cnn" / "modele.pt").exists():
        reg.append(dict(id="cnn", label="CNN", famille="réseau de neurones",
                        description=desc("Réseau convolutif appris de zéro", "cnn"), loader=CnnModel))
    if not reg:
        reg.append(dict(id="demo", label="Démo (aucun modèle entraîné)", famille="démo", description="Prédictions factices", loader=DemoModel))
    return {e["id"]: e for e in reg}


class Registry:
    def __init__(self):
        self.entries = decouvrir()
        self.cache, self.lock = {}, threading.Lock()

    @property
    def default_id(self): return next(iter(self.entries))
    @property
    def is_demo(self): return "demo" in self.entries

    def liste(self):
        return [{k: e[k] for k in ("id", "label", "description", "famille")} | {"default": e["id"] == self.default_id}
                for e in self.entries.values()]

    def get(self, model_id):
        model_id = model_id if model_id in self.entries else self.default_id
        with self.lock:
            if model_id not in self.cache:
                self.cache[model_id] = self.entries[model_id]["loader"]()
        return model_id, self.cache[model_id]

    def predict(self, model_id, text):
        model_id, m = self.get(model_id)
        k, proba, score = m.predire(text)
        ranked = sorted(zip(ORDRE, proba), key=lambda x: x[1], reverse=True)
        return {
            "category": ORDRE[k], "probability": float(proba[k]), "score": round(max(-100, min(100, score))),
            "probabilities": [{"label": l, "probability": float(p)} for l, p in ranked],
            "model": {"id": model_id, "label": self.entries[model_id]["label"]}, "demo": model_id == "demo",
        }
