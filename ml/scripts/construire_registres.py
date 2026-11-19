"""Construit un CSV (val_domaine ou train_registres) à partir de fichiers sources écrits à la main.

Format d'une ligne : type|X|R S O B P|texte     (X = classe visée : A, C, F, D)
Une ligne qui commence par « + » forme une paire contrastée avec la ligne précédente (même sujet).
Le score est calculé avec la formule officielle ; on vérifie que la classe obtenue = classe visée.
Anti-fuite : aucun 6-gramme commun avec data/test_reel.csv, aucun texte identique ; pas de doublon
avec les autres jeux passés via --exclure (ex. la validation quand on construit le train).

  python scripts/construire_registres.py data/val_domaine_sources data/val_domaine.csv --origine val_domaine
  python scripts/construire_registres.py data/train_registres_sources data/train_registres.csv --origine train_registres --exclure data/val_domaine.csv
"""
import argparse, collections, csv, glob, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from commun import ORDRE, score_vers_classe

CODES = dict(zip("ACFD", ORDRE))
POIDS = (0.333, 0.222, 0.167, 0.167, 0.111)


def mots(t): return re.findall(r"\w+", t.lower())
def norm(t): return " ".join(mots(t))
def ngrams(t, n=6):
    m = mots(t); return {tuple(m[i:i + n]) for i in range(len(m) - n + 1)}


ap = argparse.ArgumentParser()
ap.add_argument("source"); ap.add_argument("sortie"); ap.add_argument("--origine", required=True)
ap.add_argument("--exclure", nargs="*", default=[])
a = ap.parse_args()

fichiers = sorted(glob.glob(os.path.join(a.source, "*.txt"))) if os.path.isdir(a.source) else [a.source]
test = list(csv.DictReader(open("data/test_reel.csv", encoding="utf-8-sig")))
test_ng = set().union(*(ngrams(r["texte"]) for r in test)); test_norm = {norm(r["texte"]) for r in test}
autres_norm, autres_ng = set(), set()
for f in a.exclure:
    for r in csv.DictReader(open(f, encoding="utf-8-sig")):
        autres_norm.add(norm(r["texte"])); autres_ng |= ngrams(r["texte"])

rows, erreurs, retires, vus = [], [], [], set()
paire = 0
for f in fichiers:
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        l = l.strip()
        if not l or l.startswith("#"): continue
        lie = l.startswith("+"); l = l.lstrip("+").strip()
        p = l.split("|", 3)
        if len(p) != 4: erreurs.append(f"{f}:{i} format"); continue
        typ, vise, sous, texte = p
        try: R, S, O, B, P = map(int, sous.split())
        except ValueError: erreurs.append(f"{f}:{i} sous-scores illisibles"); continue
        score = round(sum(w * x for w, x in zip(POIDS, (R, S, O, B, P))))
        classe = ORDRE[score_vers_classe(score)]
        if classe != CODES[vise]:
            erreurs.append(f"{f}:{i} score {score} -> {classe} mais visé {CODES[vise]} : {texte[:50]}"); continue
        if lie and rows: pid = rows[-1]["paire_id"] or f"R{paire + 1:04d}"; rows[-1]["paire_id"] = pid
        else: pid = ""
        if pid and pid == f"R{paire + 1:04d}": paire += 1
        n, ng = norm(texte), ngrams(texte)
        raison = ("6-gramme commun avec le test" if ng & test_ng else "texte identique au test" if n in test_norm
                  else "doublon interne" if n in vus else "présent dans un jeu exclu" if n in autres_norm
                  else "6-gramme commun avec un jeu exclu" if ng & autres_ng else None)
        if raison: retires.append((raison, texte)); continue
        vus.add(n)
        rows.append(dict(texte=texte, classe=classe, score=score, R=R, S=S, O=O, B=B, P=P, type=typ, style=typ, origine=a.origine, paire_id=pid))

if erreurs:
    print("\n".join(erreurs)); sys.exit(f"{len(erreurs)} erreur(s) de cohérence : corrige les sources.")
with open(a.sortie, "w", newline="", encoding="utf-8-sig") as fo:
    w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f"{a.sortie} : {len(rows)} textes, {len(retires)} retirés, {sum(1 for r in rows if r['paire_id']) // 2} paires (approx.)")
for raison, t in retires: print(f"  retiré ({raison}) : {t[:80]}")
print("Par classe :", dict(collections.Counter(r["classe"] for r in rows)))
print("Par type   :", dict(collections.Counter(r["type"] for r in rows)))
