"""« Booster mon aura » : réécrire un texte pour lui donner le plus d'aura possible, gratuitement.

Mode par défaut, 100 % maison : aucune API externe, aucun jeton, tout tourne sur la machine.
  - Le GÉNÉRATEUR est CamemBERT en mode « texte à trous » (masked language model, almanach/camembert-base,
    le modèle de base qu'on a affiné). On masque un mot ou on insère un trou, et il propose les mots
    les plus naturels à cet endroit : la phrase reste du français correct.
  - Le JUGE est NOTRE modèle d'aura (CamemBERT affiné, SVM ou CNN, celui choisi sur le site).

Algorithme (recherche en faisceau, « beam search ») :
  1. on part du texte d'origine et d'une version nettoyée (sans excuses, emojis, « mdr », « !!! »…) ;
  2. à chaque tour, pour chacune des meilleures versions, on fabrique des variantes : supprimer un mot,
     remplacer un mot (proposé par CamemBERT), insérer un mot (proposé par CamemBERT), changer la ponctuation ;
  3. notre modèle d'aura note toutes les variantes, on garde les meilleures, et on recommence ;
  4. garde-fous de sens : les mots porteurs de sens du texte d'origine sont protégés (ni supprimés ni remplacés),
     on ne supprime que des mots « faibles » (hésitations, adverbes) et on ajoute au plus 3 mots.
On améliore donc la FORMULATION (ton, assurance, ponctuation, mot plus juste), pas le message.

Option gratuite (mode « hybride ») : si un LLM gratuit est joignable (Ollama en local par défaut, ou une API gratuite),
il propose d'abord des reformulations complètes ; CamemBERT les retouche, et c'est toujours NOTRE modèle d'aura
qui note et choisit. Réglages : AURA_LLM_URL, AURA_LLM_MODEL, AURA_LLM_KEY (voir plus bas).
"""
import os
import re
import threading

import httpx

import numpy as np

from .model import CENTRES, DEVICE

MLM = "almanach/camembert-base"
LONGUEUR_MAX = 500      # le booster vise une phrase ou un court passage
FAISCEAU = 5            # nombre de versions gardées à chaque tour
TOURS = 4
MAX_CANDIDATS = 160     # variantes notées par tour, au plus
TOP_MOTS = 4            # mots proposés par CamemBERT à chaque trou
PROBA_MIN = 0.02        # on ignore les propositions trop improbables (phrase peu naturelle)
MOTS_AJOUTES_MAX = 3    # mots nouveaux autorisés par rapport à l'original
MARGE_NATUREL = 0.35    # une retouche peut être au plus un peu moins « naturelle » que sa phrase de départ (log-probabilité moyenne)
SEUIL_CHARABIA = -5.0   # en dessous, CamemBERT juge la phrase incorrecte (mesuré : phrases correctes ≈ -1 à -4,5 ; charabia ≈ -6)
# seuls les connecteurs et adverbes peuvent être remplacés : déterminants, verbes, noms et dates restent (on garde les faits)
REMPLACABLES = {"mais", "et", "donc", "car", "ou", "or", "puis", "alors", "très", "trop", "vraiment", "plutôt", "assez",
                "bien", "tout", "toujours", "jamais", "encore", "déjà", "aussi", "même"}

# ce qui fait perdre de l'aura (cf. grille R-S-O-B-P) : se justifier, s'excuser, hésiter, abréger
MOTS_FAIBLES = r"(?:désolée?|dsl|pardon|excusez[- ]moi|excuse[- ]moi|je pense que|je crois que|en vrai|genre|" \
               r"je trouve que|j'ai l'impression que|un peu|franchement|mdr|ptdr|lol|jsp|stp|svp|frr|wesh|bref)"
# mots qu'on a le droit de supprimer (ils affaiblissent sans porter le sens)
SUPPRIMABLES = re.compile(rf"(?i)^(?:{MOTS_FAIBLES}|très|trop|vraiment|plutôt|assez|juste|carrément|grave|sûrement|"
                          r"peut-être|probablement|\w+ment|\W+)$")
OUTILS = {"le", "la", "les", "un", "une", "des", "du", "de", "ce", "cet", "cette", "ces", "est", "sont", "était", "et",
          "ou", "mais", "donc", "car", "que", "qui", "en", "au", "aux", "pour", "par", "avec", "sans", "dans", "sur",
          "très", "trop", "vraiment", "plutôt", "assez", "pas", "plus", "bien", "tout", "toute", "tous"}
EMOJIS = re.compile("[\U0001F000-\U0001FAFF☀-➿️]+")


class ErreurAmelioration(Exception):
    def __init__(self, code, message):
        super().__init__(message); self.code = code


# ------------------------------------------------------------------ générateur : CamemBERT « texte à trous »
_mlm, _verrou = None, threading.Lock()

def _charger_mlm():
    global _mlm
    with _verrou:
        if _mlm is None:
            import torch
            from transformers import AutoModelForMaskedLM, AutoTokenizer
            tok = AutoTokenizer.from_pretrained(MLM)
            _mlm = (torch, tok, AutoModelForMaskedLM.from_pretrained(MLM).to(DEVICE).eval())
    return _mlm


def _remplir_trous(phrases_a_trou):
    """phrases contenant un seul <mask> -> pour chacune, liste de (mot proposé, probabilité)."""
    torch, tok, m = _charger_mlm()
    sorties = []
    for i in range(0, len(phrases_a_trou), 32):
        lot = phrases_a_trou[i:i + 32]
        x = tok(lot, return_tensors="pt", padding=True, truncation=True, max_length=128).to(DEVICE)
        with torch.no_grad():
            logits = m(**x).logits
        for k in range(len(lot)):
            pos = (x.input_ids[k] == tok.mask_token_id).nonzero()
            if len(pos) == 0: sorties.append([]); continue
            p = logits[k, pos[0, 0]].softmax(-1)
            v, ix = p.topk(TOP_MOTS * 3)
            mots = []
            for q, j in zip(v.tolist(), ix.tolist()):
                piece = tok.convert_ids_to_tokens(j)
                mot = piece.lstrip("▁")
                # un mot entier (début de mot SentencePiece), en lettres, assez probable
                if piece.startswith("▁") and mot.isalpha() and q >= PROBA_MIN: mots.append((mot, q))
                if len(mots) == TOP_MOTS: break
            sorties.append(mots)
    return sorties


def naturel(textes):
    """Log-probabilité moyenne de chaque mot quand on le masque (pseudo-vraisemblance) : plus c'est haut,
    plus la phrase ressemble à du français normal pour CamemBERT. Sert à rejeter les variantes bancales."""
    torch, tok, m = _charger_mlm()
    phrases, cibles, qui = [], [], []
    for k, t in enumerate(textes):
        ids = tok(t, truncation=True, max_length=64)["input_ids"]
        for i in range(1, len(ids) - 1):
            masque = list(ids); masque[i] = tok.mask_token_id
            phrases.append(masque); cibles.append((i, ids[i])); qui.append(k)
    total, n = np.zeros(len(textes)), np.zeros(len(textes))
    for a in range(0, len(phrases), 64):
        lot = phrases[a:a + 64]; L = max(map(len, lot))
        x = torch.full((len(lot), L), tok.pad_token_id); att = torch.zeros((len(lot), L), dtype=torch.long)
        for j, q in enumerate(lot): x[j, :len(q)] = torch.tensor(q); att[j, :len(q)] = 1
        with torch.no_grad():
            lp = m(input_ids=x.to(DEVICE), attention_mask=att.to(DEVICE)).logits.log_softmax(-1)
        for j in range(len(lot)):
            i, cible = cibles[a + j]; k = qui[a + j]
            total[k] += float(lp[j, i, cible]); n[k] += 1
    return total / np.maximum(n, 1)


# ------------------------------------------------------------------ variantes
def _mots(t): return t.split()
def _joindre(mots): return re.sub(r"\s+([,.;:!?…])", r"\1", " ".join(mots)).strip()


def nettoyer(t):
    s = EMOJIS.sub("", t)
    s = re.sub(rf"(?i)\b{MOTS_FAIBLES}\b[,]?\s*", "", s)
    s = re.sub(r"([!?.])\1+", r"\1", s)            # « !!! » -> « ! »
    s = re.sub(r"(\w)\1{2,}", r"\1", s)             # « trooop » -> « trop »
    s = re.sub(r"\s+", " ", s).strip(" ,")
    if s and s[0].islower(): s = s[0].upper() + s[1:]
    if s and s[-1] not in ".!?…": s += "."
    return s


def _ponctuation(t):
    base = t.rstrip(".!?… ")
    out = {base + ".", base + " !", base + "…"}
    if " mais " in t: out.add(t.replace(" mais ", " : ", 1))
    if ", " in t: out.add(t.replace(", ", " : ", 1))
    return out


def _cle(w): return re.sub(r"[^\w'’-]", "", w).lower()


def _protege(w, proteges): return _cle(w) in proteges


def _variantes(t, proteges):
    """Toutes les modifications d'un mot autour du texte t (suppression, remplacement, insertion, ponctuation)."""
    mots = _mots(t)
    out = set(_ponctuation(t)) | {nettoyer(t)}
    if len(mots) > 3:
        out |= {_joindre(mots[:i] + mots[i + 1:]) for i, w in enumerate(mots) if SUPPRIMABLES.match(w) and not _protege(w, proteges)}
    # remplacement d'un mot et insertion d'un mot : CamemBERT remplit le trou
    trous, recettes = [], []
    for i, w in enumerate(mots):
        coeur = re.match(r"^(\W*)([\w'’-]+)(\W*)$", w)
        if coeur and _cle(w) in REMPLACABLES or (coeur and SUPPRIMABLES.match(w) and not _protege(w, proteges)):
            trous.append(_joindre(mots[:i] + [coeur.group(1) + "<mask>" + coeur.group(3)] + mots[i + 1:]))
            recettes.append(("remplacer", i, coeur.group(1), coeur.group(3), coeur.group(2).lower()))
    for i in range(len(mots) + 1):
        if i == len(mots) or i == 0 or mots[i - 1][-1:] in ",:;":
            trous.append(_joindre(mots[:i] + ["<mask>"] + mots[i:]))
            recettes.append(("inserer", i, "", "", None))
    for (genre, i, avant, apres, ancien), propositions in zip(recettes, _remplir_trous(trous)):
        for mot, _ in propositions:
            if genre == "remplacer" and mot.lower() != ancien:
                out.add(_joindre(mots[:i] + [avant + mot + apres] + mots[i + 1:]))
            elif genre == "inserer":
                nouveau = mot.capitalize() if i == 0 else mot
                suite = ([mots[0][0].lower() + mots[0][1:]] + mots[1:]) if i == 0 and mots else mots[i:]
                out.add(_joindre(mots[:i] + [nouveau] + suite))
    out.discard(t)
    return {v for v in out if len(v) >= 3}


def _garde_le_sens(v, proteges, mots_origine):
    mv = re.findall(r"[\w'’-]+", v.lower())
    repetition = any(a == b for a, b in zip(mv, mv[1:]))          # « merci merci », « présentation présentation »
    finie = v.rstrip()[-1:] in ".!?…"                              # pas de fragment du type « … le matin. Nous avons »
    return finie and not repetition and proteges <= set(mv) and len([m for m in mv if m not in mots_origine]) <= MOTS_AJOUTES_MAX


# ------------------------------------------------------------------ juge : notre modèle d'aura, par lots
def _scores(m, textes):
    """Score d'aura (-100..100) de chaque texte, calculé par lots."""
    if hasattr(m, "parts"):                       # ensemble CamemBERT
        torch, s = m.torch, np.zeros(len(textes))
        for w, tok, mod in m.parts:
            for i in range(0, len(textes), 32):
                lot = textes[i:i + 32]
                with torch.no_grad():
                    o = mod(**tok(lot, truncation=True, max_length=256, padding=True, return_tensors="pt").to(DEVICE)).logits.cpu().numpy()
                s[i:i + len(lot)] += w * (o[:, 0] * 100 if o.shape[1] == 1 else (np.exp(o - o.max(1, keepdims=True)) / np.exp(o - o.max(1, keepdims=True)).sum(1, keepdims=True)) @ CENTRES)
        return s
    if hasattr(m, "pipe"): return m.pipe.predict_proba(textes) @ CENTRES     # SVM
    if hasattr(m, "f"): return m.f(textes) @ CENTRES                         # CNN
    return np.array([m.predire(t)[2] for t in textes])                     # démo


# ------------------------------------------------------------------ option : un LLM gratuit propose des reformulations
# Par défaut : Ollama en local (gratuit, sans jeton ni internet). Marche aussi avec toute API gratuite au format
# « chat/completions » (Mistral, Groq, Hugging Face…) : AURA_LLM_URL + AURA_LLM_KEY + AURA_LLM_MODEL.
# AURA_LLM_MODEL vide = mode 100 % maison (CamemBERT seul).
LLM_URL = os.environ.get("AURA_LLM_URL", "http://localhost:11434/v1").rstrip("/")
LLM_MODEL = os.environ.get("AURA_LLM_MODEL", "mistral")
LLM_KEY = os.environ.get("AURA_LLM_KEY", "")
LLM_N = 6
LLM_CONSIGNE = """Tu réécris des phrases en français pour leur donner plus d'« aura » : plus d'aplomb et de charisme,
une position de force calme, une formule originale, une écriture élégante, du rythme et une chute.
Ce qui fait perdre de l'aura : se plaindre, s'excuser, hésiter, crier, les emojis, l'insulte sèche.
Règles : garder la même idée, le même sujet et les mêmes faits (ne rien inverser ni inventer) ;
à peu près la même longueur que la phrase d'origine (une ou deux phrases courtes, pas de poème) ; rien de haineux ni d'insultant ;
pas de citation célèbre existante. Réponds UNIQUEMENT par {n} réécritures différentes, une par ligne, sans numéro ni guillemets."""


def _entetes(): return {"Authorization": f"Bearer {LLM_KEY}"} if LLM_KEY else {}


# Exemples tirés de NOS données d'entraînement : paires « même sujet, faible aura -> forte aura ».
# Les montrer au LLM (few-shot) lui apprend ce que NOUS appelons de l'aura, bien mieux qu'une consigne seule.
_paires = None

def _exemples(n=6):
    global _paires
    if _paires is None:
        import pandas as pd
        from .model import ML
        _paires = []
        for f in ("paires_contrastees.csv", "train_registres.csv"):
            try:
                d = pd.read_csv(ML / "data" / f, encoding="utf-8-sig", usecols=["texte", "score", "paire_id"]).dropna()
            except Exception:
                continue
            for _, g in d.groupby("paire_id"):
                g = g.sort_values("score")
                bas, haut = g.iloc[0], g.iloc[-1]
                if haut.score >= 30 and haut.score - bas.score >= 40 and len(haut.texte) <= 160:
                    _paires.append((bas.texte, haut.texte))
    idx = np.random.default_rng().choice(len(_paires), min(n, len(_paires)), replace=False) if _paires else []
    return [_paires[i] for i in idx]


def llm_disponible():
    """Le LLM gratuit est-il joignable et le modèle demandé présent ?"""
    if not LLM_MODEL: return False
    try:
        r = httpx.get(f"{LLM_URL}/models", headers=_entetes(), timeout=3)
        ids = [m.get("id", "") for m in r.json().get("data", [])] if r.status_code == 200 else []
        return any(i == LLM_MODEL or i.split(":")[0] == LLM_MODEL for i in ids)
    except Exception:
        return False


def _propositions_llm(texte, deja_notes=None):
    demande = "Exemples (avant -> après) :\n" + "\n".join(f"- {a} -> {b}" for a, b in _exemples()) + \
              f"\n\nÀ toi. Phrase : {texte}"
    if deja_notes:
        demande += "\nVersions déjà notées par notre détecteur (score de -100 à +100), fais encore mieux :\n" + \
                   "\n".join(f"- {t} (score {sc:+.0f})" for t, sc in deja_notes)
    try:
        r = httpx.post(f"{LLM_URL}/chat/completions", headers=_entetes(), timeout=90, json={
            "model": LLM_MODEL, "temperature": 0.9,
            "messages": [{"role": "system", "content": LLM_CONSIGNE.format(n=LLM_N)}, {"role": "user", "content": demande}]})
        r.raise_for_status()
        contenu = r.json()["choices"][0]["message"]["content"]
    except Exception:
        return []                                  # le LLM n'est qu'une aide : sans lui, on continue en local
    # on enlève numéros, puces et scores recopiés (« 1. », « - », « +8 : », « Citation +34 : »)
    prefixe = r"^\s*(?:[-*•]|(?:citation\s*)?\d+\s*[.)\-–:]|(?:\w+\s*)?\(?(?:score\s*)?[+-]?\d+\)?\s*:)\s*"
    lignes = [re.sub(prefixe, "", re.sub(prefixe, "", l), flags=re.I).strip().strip('"«» ') for l in contenu.splitlines()]
    lignes = [re.sub(r"\s*\((?:score\s*)?[+-]?\d+\)\s*$", "", l, flags=re.I) for l in lignes]
    lignes = [nettoyer(l) if EMOJIS.search(l) else l for l in lignes]      # pas d'emojis
    longueur_max = 2 * len(texte) + 60                      # une reformulation, pas un poème ni un commentaire
    phrases = lambda l: len(re.findall(r"[.!?…]+(?:\s|$)", l))
    return [l for l in lignes if 3 <= len(l) <= longueur_max and phrases(l) <= 2 and '"' not in l
            and l.rstrip()[-1:] in ".!?…"][:LLM_N * 2]     # phrase terminée, pas un morceau coupé


# ------------------------------------------------------------------ recherche en faisceau
def _proteges_de(t):
    """Mots porteurs de sens : ni mots outils, ni mots faibles."""
    return {_cle(w) for w in _mots(nettoyer(t)) if _cle(w) and _cle(w) not in OUTILS and not SUPPRIMABLES.match(w)}


def ameliorer(registry, model_id, texte):
    texte = texte.strip()
    if len(texte) > LONGUEUR_MAX:
        raise ErreurAmelioration(400, f"Le booster marche sur une phrase ou un court passage ({LONGUEUR_MAX} caractères max).")
    model_id, juge = registry.get(model_id)
    try:
        _charger_mlm()
    except Exception as e:
        raise ErreurAmelioration(503, f"Générateur indisponible : impossible de charger {MLM} ({e.__class__.__name__}).") from e

    notes, racine, naturels, regles = {}, {}, {}, {}
    def noter(textes):
        nouveaux = [t for t in dict.fromkeys(textes) if t not in notes]
        if nouveaux:
            notes.update(zip(nouveaux, _scores(juge, nouveaux).tolist()))
    def nouvelle_racine(t):
        """Point de départ d'une lignée de retouches : ses mots porteurs de sens seront protégés."""
        racine[t] = t; naturels[t] = True
        regles[t] = (_proteges_de(t), set(re.findall(r"[\w'’-]+", t.lower())), float(naturel([t])[0]) - MARGE_NATUREL)

    depart = nettoyer(texte) or texte
    noter([texte, depart]); nouvelle_racine(depart)
    mode = "local"

    # 1) option LLM gratuit : il propose des reformulations complètes, notre modèle les note
    if llm_disponible():
        seuil_llm = SEUIL_CHARABIA                        # on écarte seulement les propositions vraiment bancales
        for tour in range(2):
            deja = sorted(((t, notes[t]) for t in regles), key=lambda x: -x[1])[:4] if tour else None
            props = [p for p in dict.fromkeys(_propositions_llm(texte, deja)) if p not in notes]
            if props:
                props = [p for p, nat in zip(props, naturel(props)) if nat >= seuil_llm]
            noter(props)
            for p in props: nouvelle_racine(p)
            if props: mode = "hybride"

    # 2) retouches mot à mot par CamemBERT autour des meilleures versions (recherche en faisceau)
    def choisir_faisceau():
        """Les FAISCEAU versions les mieux notées parmi celles qui restent naturelles."""
        garde = []
        for t in sorted(notes, key=notes.get, reverse=True):
            if t == texte or t not in racine: continue
            if t not in naturels:
                naturels[t] = bool(naturel([t])[0] >= regles[racine[t]][2])
            if naturels[t]: garde.append(t)
            if len(garde) == FAISCEAU: break
        return garde or [depart]
    faisceau = choisir_faisceau()
    for _ in range(TOURS if mode == "local" else 2):       # avec un LLM, les retouches servent juste à peaufiner
        candidats = {}
        for t in faisceau:
            proteges, mots_origine, _ = regles[racine[t]]
            for v in _variantes(t, proteges):
                if v not in notes and _garde_le_sens(v, proteges, mots_origine): candidats.setdefault(v, racine[t])
        if not candidats: break
        liste = sorted(candidats)
        if len(liste) > MAX_CANDIDATS:                     # on limite le nombre de variantes notées par tour
            liste = list(np.random.default_rng(len(notes)).choice(liste, MAX_CANDIDATS, replace=False))
        for v in liste: racine[v] = candidats[v]
        noter(liste)
        faisceau = choisir_faisceau()

    # les meilleures versions sont renotées une par une, exactement comme un scan normal du site
    # on montre des propositions DIFFÉRENTES entre elles (pas 5 fois la même phrase à un mot près) :
    # au plus une par lignée (une reformulation du LLM et ses retouches), et pas deux trop ressemblantes
    def ressemblance(a, b):
        ma, mb = set(re.findall(r"\w+", a.lower())), set(re.findall(r"\w+", b.lower()))
        return len(ma & mb) / max(1, len(ma | mb))
    meilleures, lignees = [], set()
    for t in sorted(notes, key=notes.get, reverse=True):
        if not naturels.get(t) or t == texte or racine.get(t) in lignees: continue
        if any(ressemblance(t, m) > 0.6 for m in meilleures): continue
        meilleures.append(t); lignees.add(racine.get(t))
        if len(meilleures) == 6: break
    meilleures = meilleures or [depart]
    original = registry.predict(model_id, texte)
    resultats = sorted(((t, registry.predict(model_id, t)) for t in meilleures), key=lambda x: -x[1]["score"])
    resume = lambda t, r: {"texte": t, "category": r["category"], "score": r["score"], "probability": r["probability"]}
    meilleur_t, meilleur_r = resultats[0]
    return {
        "original": resume(texte, original),
        "meilleur": resume(meilleur_t, meilleur_r) | {"probabilities": meilleur_r["probabilities"]},
        "gain": meilleur_r["score"] - original["score"],
        "autres": [resume(t, r) for t, r in resultats[1:]],
        "n_essais": len(notes) - 1,
        "model": original["model"],
        "mode": mode,
        "generateur": f"{LLM_MODEL} (gratuit, local) + CamemBERT" if mode == "hybride" else "CamemBERT (100 % local)",
    }
