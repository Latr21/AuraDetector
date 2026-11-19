"""Construit data/train_joutes_reelles.csv (textes du domaine public, Wikisource) à partir de data/joutes_sources/*.txt.

Format : X|R S O B P|auteur — œuvre|url|texte verbatim
Contrôle de chevauchement STRICT avec le test (qui contient aussi du théâtre classique) : on retire tout texte
qui partage un 5-gramme avec le test, est identique, ou dont la version normalisée contient / est contenue dans
un texte du test (dès 3 mots). La liste des retraits est imprimée et écrite dans results/joutes_retirees.txt.
"""
import csv, glob, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from commun import ORDRE, score_vers_classe

CODES = dict(zip("ACFD", ORDRE)); POIDS = (0.333, 0.222, 0.167, 0.167, 0.111)
def mots(t): return re.findall(r"\w+", t.lower().replace("’", "'"))
def norm(t): return " ".join(mots(t))
def ngrams(t, n): m = mots(t); return {tuple(m[i:i + n]) for i in range(len(m) - n + 1)}

test = list(csv.DictReader(open("data/test_reel.csv", encoding="utf-8-sig")))
t_ng = set().union(*(ngrams(r["texte"], 5) for r in test)); t_norm = [norm(r["texte"]) for r in test]
rows, retires, erreurs = [], [], []
for f in sorted(glob.glob("data/joutes_sources/*.txt")):
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        l = l.strip()
        if not l or l.startswith("#"): continue
        p = l.split("|", 4)
        if len(p) != 5: erreurs.append(f"{f}:{i} format"); continue
        vise, sous, auteur, url, texte = p
        sc = round(sum(w * int(x) for w, x in zip(POIDS, sous.split())))
        cl = ORDRE[score_vers_classe(sc)]
        if cl != CODES[vise]: erreurs.append(f"{f}:{i} score {sc} -> {cl} ≠ {CODES[vise]}"); continue
        n = norm(texte)
        raison = None
        if ngrams(texte, 5) & t_ng: raison = "5-gramme commun avec le test"
        elif n in t_norm: raison = "texte identique au test"
        elif len(n.split()) >= 3 and any(n in t or (len(t.split()) >= 3 and t in n) for t in t_norm):
            raison = "inclus dans un texte du test (ou l'inverse)"
        if raison: retires.append(f"{raison} : [{auteur}] {texte}"); continue
        rows.append(dict(texte=texte, classe=cl, score=sc, style="joute_classique", origine="joutes_reelles", source=url, auteur=auteur))
if erreurs: sys.exit("\n".join(erreurs))
with open("data/train_joutes_reelles.csv", "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
os.makedirs("results", exist_ok=True)
open("results/joutes_retirees.txt", "w", encoding="utf-8").write("\n".join(retires) + "\n")
import collections
print(f"train_joutes_reelles.csv : {len(rows)} textes gardés, {len(retires)} retirés")
for r in retires: print("  retiré —", r)
print("Par classe :", dict(collections.Counter(r["classe"] for r in rows)))
print("Par auteur :", dict(collections.Counter(r["auteur"].split(" — ")[0] for r in rows)))
