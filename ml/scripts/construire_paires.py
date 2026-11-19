"""Assemble data/paires_sources/*.txt en data/paires_contrastees.csv et filtre toute fuite vers le test réel.

Format source (une paire par ligne) : style|X score|texte A|Y score|texte B   (X,Y ∈ A,C,F,D)
Contrôle anti-fuite : on retire la paire entière si un de ses textes partage une séquence de 6 mots
avec un texte de data/test_reel.csv, ou est identique (normalisé) à un texte court du test.
"""
import csv, glob, re, sys, collections

CODES = {"A": "Anti-Aura", "C": "Aura Correcte", "F": "Forte Aura", "D": "Aura Divine"}
SEUILS = {"Anti-Aura": (-100, -11), "Aura Correcte": (-10, 24), "Forte Aura": (25, 74), "Aura Divine": (75, 100)}


def mots(t): return re.findall(r"\w+", t.lower())
def norm(t): return " ".join(mots(t))
def ngrams(t, n=6):
    m = mots(t); return {tuple(m[i:i + n]) for i in range(len(m) - n + 1)}


test = list(csv.DictReader(open("data/test_reel.csv", encoding="utf-8-sig")))
test_ng = set().union(*(ngrams(r["texte"]) for r in test))
test_norm = {norm(r["texte"]) for r in test}

paires, erreurs = [], []
for f in sorted(glob.glob("data/paires_sources/*.txt")):
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        l = l.strip()
        if not l or l.startswith("#"): continue
        p = l.split("|")
        if len(p) != 5: erreurs.append(f"{f}:{i} champs={len(p)}"); continue
        style, ca, ta, cb, tb = p
        out = []
        for c, t in ((ca, ta), (cb, tb)):
            k, s = c.split(); cl = CODES[k]; s = int(s)
            lo, hi = SEUILS[cl]
            if not lo <= s <= hi: erreurs.append(f"{f}:{i} score {s} hors de {cl}")
            out.append(dict(texte=t.strip(), classe=cl, score=s, style=style))
        paires.append(out)
if erreurs: sys.exit("\n".join(erreurs))

garde, retirees, vus = [], [], set()
for p in paires:
    raison = None
    for r in p:
        if ngrams(r["texte"]) & test_ng: raison = "6-gramme commun avec le test"
        elif norm(r["texte"]) in test_norm: raison = "texte identique au test"
        elif norm(r["texte"]) in vus: raison = "doublon interne"
    if raison: retirees.append((raison, p)); continue
    vus.update(norm(r["texte"]) for r in p); garde.append(p)

with open("data/paires_contrastees.csv", "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=["texte", "classe", "score", "style", "origine", "paire_id"])
    w.writeheader()
    for k, p in enumerate(garde, 1):
        for r in p: w.writerow({**r, "origine": "paires_contrastees", "paire_id": f"P{k:03d}"})

print(f"{len(paires)} paires lues, {len(retirees)} retirées, {len(garde)} gardées ({2 * len(garde)} textes)")
for raison, p in retirees: print(f"  retirée ({raison}) : {p[0]['texte'][:60]} / {p[1]['texte'][:60]}")
c = collections.Counter(r["classe"] for p in garde for r in p)
print("Par classe :", dict(c)); print("Par style :", dict(collections.Counter(p[0]["style"] for p in garde)))
