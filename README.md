# Aura Detector

Détecte l'« aura » d'un texte (Anti-Aura, Aura Correcte, Forte Aura, Aura Divine) avec trois modèles : SVM, CNN et CamemBERT. Interface web animée, booster d'aura local et gratuit.

## Installation

Python 3.13 recommandé.

```powershell
# depuis la racine du projet
python -m venv ml/.venv
ml\.venv\Scripts\activate          # Windows
# source ml/.venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Au premier lancement, CamemBERT est téléchargé depuis Hugging Face (voir `ml/hf_repo.txt`). Le SVM et le CNN sont déjà dans le dépôt.

## Lancer l'application

**Version FastAPI + frontend (recommandée)**

```powershell
python -m uvicorn backend.app:app --reload --port 8000
```

Puis ouvrir http://localhost:8000.

Sans activer le venv : `ml\.venv\Scripts\python.exe -m uvicorn backend.app:app --port 8000`.

**Version Streamlit**

```powershell
streamlit run streamlit_app.py
```

## Vérifier que ça tourne

```powershell
curl http://localhost:8000/api/health   # {"ok":true,"demo":false,"default_model":"camembert"}
curl http://localhost:8000/api/models   # liste des modèles disponibles
```

## Entraînement des modèles

Le kit d'entraînement, le notebook et les résultats sont dans [ml/](ml/README.md).

## Structure

```
backend/     API FastAPI (prédiction, extraction de texte, booster)
frontend/    interface web (index.html, app.js, style.css)
Assets/      GIFs de réaction par catégorie
ml/          entraînement, modèles, notebook, résultats
docs/        rapport du projet
streamlit_app.py   version Streamlit
```
