"""Accord inter-annotateurs pour Aura Classifier.
Usage : python3 accord.py annotateur1.csv annotateur2.csv
Chaque fichier : colonnes id, classe (et score facultatif)."""
import csv, sys
from sklearn.metrics import cohen_kappa_score, confusion_matrix
ORDRE = ["Anti-Aura", "Aura Correcte", "Forte Aura", "Aura Divine"]
COURT = ["Anti", "Corr", "Fort", "Divi"]

def lire(p):
    return {r["id"]: r for r in csv.DictReader(open(p, encoding="utf-8-sig")) if r.get("classe", "").strip()}

a, b = lire(sys.argv[1]), lire(sys.argv[2])
ids = sorted(set(a) & set(b))
if not ids: sys.exit("Aucun texte annoté en commun (colonne 'classe' vide ?).")
for i in ids:
    for d, p in ((a, sys.argv[1]), (b, sys.argv[2])):
        if d[i]["classe"] not in ORDRE: sys.exit(f"Classe inconnue '{d[i]['classe']}' pour {i} dans {p}")
ya = [ORDRE.index(a[i]["classe"]) for i in ids]
yb = [ORDRE.index(b[i]["classe"]) for i in ids]
print(f"Textes en commun : {len(ids)}")
print(f"Accord exact           : {sum(x == y for x, y in zip(ya, yb)) / len(ids):.1%}")
print(f"Accord à ±1 classe     : {sum(abs(x - y) <= 1 for x, y in zip(ya, yb)) / len(ids):.1%}")
k = cohen_kappa_score(ya, yb, weights="quadratic", labels=list(range(4)))
lect = "très bon" if k >= .8 else "correct" if k >= .6 else "faible"
print(f"Kappa pondéré (quadr.) : {k:.3f}  -> accord {lect}")
try:
    sa = [float(a[i]["score"]) for i in ids]; sb = [float(b[i]["score"]) for i in ids]
    from scipy.stats import spearmanr
    print(f"Corrélation des scores (Spearman) : {spearmanr(sa, sb).statistic:.3f}")
    print(f"Écart moyen de score : {sum(abs(x - y) for x, y in zip(sa, sb)) / len(ids):.1f} points")
except (KeyError, ValueError, ImportError):
    pass
print("\nMatrice (lignes = annotateur 1, colonnes = annotateur 2)")
m = confusion_matrix(ya, yb, labels=list(range(4)))
print("      " + " ".join(f"{c:>5}" for c in COURT))
for c, row in zip(COURT, m): print(f"{c:>5} " + " ".join(f"{v:>5}" for v in row))
gros = [(i, a[i]["classe"], b[i]["classe"]) for i, x, y in zip(ids, ya, yb) if abs(x - y) >= 2]
print(f"\nDésaccords de 2 classes ou plus : {len(gros)}")
for i, ca, cb in gros:
    print(f"  {i} | {ca} vs {cb} | {a[i].get('texte', b[i].get('texte', ''))[:90]!r}")
