"""Héberge l'ensemble CamemBERT (~2,6 Go, trop gros pour GitHub) sur le Hugging Face Hub.

    python ml/scripts/hf_modeles.py envoyer [--repo user/nom] [--prive]   # upload (après `hf auth login`)
    python ml/scripts/hf_modeles.py telecharger [--repo user/nom]         # download dans ml/models/

Le dépôt HF reproduit l'arborescence locale : <composant>/final/{config.json, model.safetensors, tokenizer*.json}.
Seuls les composants de l'ensemble retenu (ml/results/p2_choix.json) sont envoyés.
L'identifiant du dépôt est lu dans AURA_HF_REPO, sinon dans ml/hf_repo.txt (écrit par `envoyer`).
"""
import argparse
import json
import os
from pathlib import Path

ML = Path(__file__).resolve().parent.parent
MODELS = ML / "models"
REPO_FILE = ML / "hf_repo.txt"
FICHIERS = ["config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json",
            "sentencepiece.bpe.model", "special_tokens_map.json"]


def repo_id():
    r = os.environ.get("AURA_HF_REPO")
    if r is None and REPO_FILE.exists():
        r = REPO_FILE.read_text(encoding="utf-8").strip()
    return r or None


def composants():
    choix = json.loads((ML / "results" / "p2_choix.json").read_text(encoding="utf-8"))
    retenu = choix["candidats"][choix["meilleur"]]
    return [n for n, w in retenu["composants"].items() if n != "tfidf" and w > 0]


def manquants():
    return [n for n in composants() if not (MODELS / n / "final" / "model.safetensors").exists()]


def telecharger(repo=None, noms=None):
    """Télécharge les composants manquants (ou `noms`) depuis le Hub dans ml/models/. Renvoie True si tout est là."""
    from huggingface_hub import snapshot_download
    repo = repo or repo_id()
    noms = noms if noms is not None else manquants()
    if not noms:
        return True
    if not repo:
        raise RuntimeError("aucun dépôt Hugging Face configuré (AURA_HF_REPO ou ml/hf_repo.txt)")
    print(f"[aura] téléchargement de {', '.join(noms)} depuis huggingface.co/{repo} (≈2,6 Go la 1re fois)…", flush=True)
    snapshot_download(repo, local_dir=MODELS, allow_patterns=[f"{n}/final/*" for n in noms])
    return not manquants()


def envoyer(repo=None, prive=False):
    from huggingface_hub import HfApi
    api = HfApi()
    repo = repo or repo_id() or f"{api.whoami()['name']}/aura-detector-camembert"
    noms = composants()
    absents = manquants()
    if absents:
        raise SystemExit(f"modèles absents en local : {absents}")
    api.create_repo(repo, repo_type="model", private=prive, exist_ok=True)
    carte = MODELS / "README.md"
    carte.write_text(CARTE.format(repo=repo, liste="\n".join(f"- `{n}/final`" for n in noms)), encoding="utf-8")
    print(f"[aura] envoi de {len(noms)} modèles vers huggingface.co/{repo}…", flush=True)
    api.upload_folder(repo_id=repo, folder_path=MODELS, commit_message="Ensemble CamemBERT Aura Detector",
                      allow_patterns=["README.md"] + [f"{n}/final/{f}" for n in noms for f in FICHIERS])
    carte.unlink()
    REPO_FILE.write_text(repo + "\n", encoding="utf-8")
    print(f"[aura] ok : https://huggingface.co/{repo}  (identifiant écrit dans {REPO_FILE.relative_to(ML.parent)})")


CARTE = """---
language: fr
library_name: transformers
base_model: almanach/camembert-base
tags: [text-classification, french, camembert]
---
# Aura Detector — ensemble CamemBERT

Modèles fine-tunés du projet Aura Detector (score d'« aura » d'un texte français, 4 classes :
Anti-Aura, Aura Correcte, Forte Aura, Aura Divine). L'ensemble pondéré et les seuils sont dans
`ml/results/p2_choix.json` du dépôt du projet.

{liste}

```python
from huggingface_hub import snapshot_download
snapshot_download("{repo}", local_dir="ml/models")
```
"""


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("action", choices=["envoyer", "telecharger"])
    p.add_argument("--repo", help="identifiant du dépôt HF, ex. utilisateur/aura-detector-camembert")
    p.add_argument("--prive", action="store_true", help="dépôt privé (il faudra alors un token pour télécharger)")
    a = p.parse_args()
    if a.action == "envoyer":
        envoyer(a.repo, a.prive)
    else:
        ok = telecharger(a.repo)
        print("[aura] modèles prêts" if ok else "[aura] il manque encore des modèles")
