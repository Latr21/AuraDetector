"""API Aura Detector — lancer avec : uvicorn backend.app:app --reload"""
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .ameliorer import ErreurAmelioration, ameliorer
from .extract import extract_text
from .model import Registry

FRONT = Path(__file__).resolve().parent.parent / "frontend"
ASSETS = Path(__file__).resolve().parent.parent / "Assets"
# dossier de GIFs par classe d'aura
GIF_DIRS = {"Anti-Aura": "Anti_Aura", "Aura Correcte": "Aura_normal", "Forte Aura": "Forte_Aura", "Aura Divine": "Aura_legendaire"}
MAX_BYTES = 10 * 1024 * 1024

app = FastAPI(title="Aura Detector")
registry = Registry()


@app.get("/api/health")
def health():
    return {"ok": True, "demo": registry.is_demo, "default_model": registry.default_id}


@app.get("/api/gifs")
def gifs():
    out = {}
    for classe, dossier in GIF_DIRS.items():
        d = ASSETS / dossier
        out[classe] = [f"/assets/{dossier}/{f.name}" for f in sorted(d.glob("*.gif"))] if d.exists() else []
    return out


@app.get("/api/models")
def models():
    return registry.liste()


@app.post("/api/predict")
async def api_predict(text: str = Form(""), model: str = Form(""), file: UploadFile | None = File(None)):
    filename = None
    if file is not None and file.filename:
        data = await file.read()
        if len(data) > MAX_BYTES:
            raise HTTPException(413, "Fichier trop lourd (10 Mo max), même pour une aura légendaire.")
        try:
            text = extract_text(file.filename, data)
        except Exception as e:
            raise HTTPException(422, f"Impossible de lire ce fichier : {e}")
        filename = file.filename
    text = (text or "").strip()
    if len(text) < 3:
        raise HTTPException(400, "Aucun texte détecté. Même le vide a plus d'aura que ça.")
    try:   # chargement du modèle + inférence hors de la boucle asynchrone
        result = await run_in_threadpool(registry.predict, model, text)
    except Exception as e:
        raise HTTPException(500, f"Le modèle a perdu son aura : {e}")
    result.update(filename=filename, n_chars=len(text), preview=text[:280])
    return result


@app.post("/api/improve")
async def api_improve(text: str = Form(""), model: str = Form("")):
    """Réécrit le texte pour maximiser son aura (un LLM propose, notre modèle note et choisit)."""
    text = (text or "").strip()
    if len(text) < 3:
        raise HTTPException(400, "Rien à booster : écris d'abord une phrase.")
    try:
        return await run_in_threadpool(ameliorer, registry, model, text)
    except ErreurAmelioration as e:
        raise HTTPException(e.code, str(e))
    except Exception as e:
        raise HTTPException(500, f"Le booster a perdu son aura : {e}")


app.mount("/static", StaticFiles(directory=FRONT), name="static")
if ASSETS.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS), name="assets")


@app.get("/")
def index():
    return FileResponse(FRONT / "index.html")
