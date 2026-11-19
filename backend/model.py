"""Chargement du modèle de classification.

Le notebook doit sauvegarder un pipeline scikit-learn (ex: TfidfVectorizer + LogisticRegression)
avec :  joblib.dump(pipeline, "models/model.joblib")
Le pipeline doit exposer predict_proba() et classes_.

Tant que ce fichier n'existe pas, un modèle "démo" renvoie des probabilités factices
pour pouvoir développer l'interface.
"""
import hashlib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "model.joblib"

DEMO_LABELS = ["Sport", "Politique", "Tech", "Business", "Divertissement"]


class DemoModel:
    classes_ = DEMO_LABELS
    is_demo = True

    def predict_proba(self, texts):
        out = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            raw = [h[i] + 1 for i in range(len(self.classes_))]
            top = max(range(len(raw)), key=raw.__getitem__)
            raw[top] *= 4  # un gagnant franc, c'est plus fun
            s = sum(raw)
            out.append([r / s for r in raw])
        return out


def load_model():
    if MODEL_PATH.exists():
        import joblib
        m = joblib.load(MODEL_PATH)
        m.is_demo = False
        return m
    return DemoModel()


def predict(model, text: str):
    probs = list(model.predict_proba([text])[0])
    labels = [str(c) for c in model.classes_]
    ranked = sorted(zip(labels, probs), key=lambda x: x[1], reverse=True)
    return {
        "category": ranked[0][0],
        "probability": float(ranked[0][1]),
        "probabilities": [{"label": l, "probability": float(p)} for l, p in ranked],
        "demo": getattr(model, "is_demo", False),
    }
