"""API Aura Detector — lancer avec : uvicorn backend.app:app --reload"""
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .extract import extract_text
from .model import load_model, predict

FRONT = Path(__file__).resolve().parent.parent / "frontend"
MAX_BYTES = 10 * 1024 * 1024

app = FastAPI(title="Aura Detector")
model = load_model()


@app.get("/api/health")
def health():
    return {"ok": True, "labels": [str(c) for c in model.classes_], "demo": getattr(model, "is_demo", False)}


@app.post("/api/predict")
async def api_predict(text: str = Form(""), file: UploadFile | None = File(None)):
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
    result = predict(model, text)
    result.update(filename=filename, n_chars=len(text), preview=text[:280])
    return result


app.mount("/static", StaticFiles(directory=FRONT), name="static")


@app.get("/")
def index():
    return FileResponse(FRONT / "index.html")
