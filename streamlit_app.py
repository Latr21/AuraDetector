"""Aura Detector, version Streamlit (Streamlit Community Cloud).

Lancer en local : streamlit run streamlit_app.py
Même registre de modèles que l'API FastAPI (backend/model.py) : CamemBERT (ensemble retenu), SVM et CNN.
CamemBERT est téléchargé depuis le Hugging Face Hub au premier lancement (ml/hf_repo.txt) ; si le dépôt est privé,
il faut un secret HF_TOKEN (Streamlit Cloud : Settings → Secrets).
"""
import os
import random
from pathlib import Path

import streamlit as st

# Streamlit Cloud est limité en RAM : CamemBERT en bfloat16 (~2 Go au lieu de 3,3, mêmes prédictions).
os.environ.setdefault("AURA_DTYPE", "bfloat16")
try:  # secrets Streamlit (HF_TOKEN…) → variables d'environnement lues par huggingface_hub
    for k, v in st.secrets.items():
        if isinstance(v, str):
            os.environ.setdefault(k, v)
except Exception:
    pass
from backend.extract import extract_text  # noqa: E402
from backend.model import ORDRE, Registry  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "Assets"
GIF_DIRS = {"Anti-Aura": "Anti_Aura", "Aura Correcte": "Aura_normal", "Forte Aura": "Forte_Aura", "Aura Divine": "Aura_legendaire"}
EMOJI = {"Anti-Aura": "💀", "Aura Correcte": "😐", "Forte Aura": "🔥", "Aura Divine": "👑"}
MAX_BYTES = 10 * 1024 * 1024

st.set_page_config(page_title="Aura Detector", page_icon="🔮", layout="centered")


@st.cache_resource(show_spinner="Préparation des modèles (premier lancement : téléchargement de CamemBERT, ~2 min)…")
def registre():
    return Registry()


st.title("🔮 AURA DETECTOR")
st.caption("Ton texte a-t-il de l'aura ? Notre IA ne ment jamais*")

reg = registre()
if reg.is_demo:
    st.warning("Mode démo : aucun modèle entraîné n'a été trouvé, les prédictions sont factices.")

modeles = reg.liste()
choix = st.selectbox("🧠 Modèle", modeles, format_func=lambda m: m["label"],
                     index=next(i for i, m in enumerate(modeles) if m["default"]))
st.caption(choix["description"])

onglet_texte, onglet_fichier = st.tabs(["✍️ Texte", "📂 Fichier"])
with onglet_texte:
    texte = st.text_area("Ton texte", height=180, placeholder="Colle ton texte ici et laisse l'univers décider…",
                         label_visibility="collapsed")
with onglet_fichier:
    fichier = st.file_uploader("PDF, DOCX, PPTX, TXT, MD, HTML, JSON, CSV…", label_visibility="visible")

if st.button("⚡ SCANNER L'AURA ⚡", type="primary", width="stretch"):
    nom = None
    if fichier is not None:
        data = fichier.getvalue()
        if len(data) > MAX_BYTES:
            st.error("Fichier trop lourd (10 Mo max), même pour une aura légendaire."); st.stop()
        try:
            texte, nom = extract_text(fichier.name, data), fichier.name
        except Exception as e:
            st.error(f"Impossible de lire ce fichier : {e}"); st.stop()
    texte = (texte or "").strip()
    if len(texte) < 3:
        st.error("Aucun texte détecté. Même le vide a plus d'aura que ça."); st.stop()

    with st.spinner("Scan de l'aura en cours…"):  # le registre garde les modèles chargés en cache
        r = reg.predict(choix["id"], texte)

    cat = r["category"]
    st.divider()
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader(f"{EMOJI[cat]} {cat}")
        st.metric("Score d'aura", f"{r['score']:+d} / 100")
        st.progress((r["score"] + 100) / 200)
        for p in sorted(r["probabilities"], key=lambda p: ORDRE.index(p["label"])):
            st.write(f"{EMOJI[p['label']]} {p['label']} : **{p['probability']:.0%}**")
            st.progress(p["probability"])
    with col2:
        gifs = sorted((ASSETS / GIF_DIRS[cat]).glob("*.gif"))
        if gifs:
            st.image(str(random.choice(gifs)), width="stretch")
    st.caption(f"Modèle : {r['model']['label']} · {len(texte)} caractères" + (f" · {nom}" if nom else ""))
    with st.expander("Texte analysé"):
        st.write(texte[:2000] + ("…" if len(texte) > 2000 else ""))

st.caption("*Si, parfois.")
