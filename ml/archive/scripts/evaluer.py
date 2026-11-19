"""Évaluation comparative sur le test réel : tableau, matrice du meilleur modèle, pires erreurs,
comparaison pré-entraîné vs entraîné de zéro (par classe et par type de texte). Écrit results/evaluation.md."""
import csv, json, os, shutil, sys

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score

sys.path.insert(0, os.path.dirname(__file__))
from commun import ORDRE, COURT, metriques

test = {r["id"]: r for r in csv.DictReader(open("data/test_reel.csv", encoding="utf-8-sig"))}

# CamemBERT écrit ses prédictions dans models/<run>/ : on les recopie dans results/
for run in ("camembert_classif", "camembert_regression", "camembert_classif_pondere"):
    src = f"models/{run}/predictions_test_reel.csv"
    if os.path.exists(src):
        shutil.copy(src, f"results/predictions_{run}.csv")
        d = json.load(open(f"models/{run}/resultats.json", encoding="utf-8")); json.dump(d, open(f"results/{run}.json", "w", encoding="utf-8"), indent=2)

MODELES = [  # (nom affiché, fichier json, fichier prédictions, colonne, clé temps, clé params, pré-entraîné ?)
    ("Baseline TF-IDF+LR (synthétique seul)", "baseline", "baseline", "prediction_classif", "classification", False),
    ("Baseline régression Ridge (synthétique seul)", "baseline", "baseline", "prediction_regression", "regression", False),
    ("Baseline + Grok + paires (classif)", "baseline_paires", "baseline_paires", "prediction_classif", "classification", False),
    ("Baseline + Grok + paires (régression)", "baseline_paires", "baseline_paires", "prediction_regression", "regression", False),
    ("CamemBERT classification", "camembert_classif", "camembert_classif", "prediction", None, True),
    ("CamemBERT classification pondérée", "camembert_classif_pondere", "camembert_classif_pondere", "prediction", None, True),
    ("CamemBERT régression", "camembert_regression", "camembert_regression", "prediction", None, True),
    ("MLP NumPy (de zéro)", "mlp_numpy", "mlp_numpy", "prediction", None, False),
    ("BiLSTM classification (de zéro)", "bilstm_classif", "bilstm_classif", "prediction", None, False),
    ("BiLSTM régression (de zéro)", "bilstm_regression", "bilstm_regression", "prediction", None, False),
]

lignes, preds = [], {}
for nom, fj, fp, col, cle, pre in MODELES:
    if not os.path.exists(f"results/predictions_{fp}.csv"): print("absent :", nom); continue
    rows = list(csv.DictReader(open(f"results/predictions_{fp}.csv", encoding="utf-8-sig")))
    ids = [r["id"] for r in rows]; y = np.array([ORDRE.index(test[i]["classe"]) for i in ids])
    p = np.array([ORDRE.index(r[col]) for r in rows])
    d = json.load(open(f"results/{fj}.json", encoding="utf-8"))
    t = d["temps_entrainement_s"][cle] if cle else d["temps_entrainement_s"]
    n = d["n_parametres"][cle] if cle else d["n_parametres"]
    lignes.append(dict(nom=nom, pre=pre, t=t, n=n, **metriques(y, p))); preds[nom] = (ids, y, p)


def duree(s): return f"{s:.0f} s" if s < 120 else f"{s / 60:.1f} min"


out = ["## Tableau comparatif (test réel, 330 textes)\n",
       "| Modèle | Exactitude | ±1 classe | F1-macro | Kappa quadratique | Temps d'entraînement | Paramètres |",
       "|---|---|---|---|---|---|---|",
       "| Toujours « Aura Correcte » | 57.9 % | 90.0 % | 0.18 | 0.00 | – | – |"]
for l in lignes:
    out.append(f"| {l['nom']} | {l['accuracy']:.1%} | {l['a_une_classe_pres']:.1%} | {l['f1_macro']:.2f} | **{l['kappa_quadratique']:.3f}** | {duree(l['t'])} | {l['n']:,} |".replace(",", " "))

best = max(lignes, key=lambda l: l["kappa_quadratique"])
best_zero = max([l for l in lignes if not l["pre"] and "Baseline" not in l["nom"]], key=lambda l: l["kappa_quadratique"])
best_pre = max([l for l in lignes if l["pre"]], key=lambda l: l["kappa_quadratique"])


def matrice(nom):
    ids, y, p = preds[nom]; m = confusion_matrix(y, p, labels=range(4))
    s = ["| réf. \\ prédit | " + " | ".join(COURT) + " |", "|---|---|---|---|---|"]
    s += [f"| **{c}** | " + " | ".join(str(v) for v in row) + " |" for c, row in zip(COURT, m)]
    return s


out += [f"\n## Matrice de confusion du meilleur modèle : {best['nom']}\n"] + matrice(best["nom"])
out += [f"\n## Matrice de confusion du meilleur modèle entraîné de zéro : {best_zero['nom']}\n"] + matrice(best_zero["nom"])

ids, y, p = preds[best["nom"]]
ordre = sorted(range(len(ids)), key=lambda i: (-abs(int(y[i]) - int(p[i])), ids[i]))[:15]
out += [f"\n## 15 pires erreurs ({best['nom']})\n", "| id | type | texte | référence | prédiction |", "|---|---|---|---|---|"]
for i in ordre:
    r = test[ids[i]]; t = r["texte"].replace("|", "/").replace("\n", " ")
    out.append(f"| {ids[i]} | {r['type']} | {t[:160]}{'…' if len(t) > 160 else ''} | {ORDRE[y[i]]} | {ORDRE[p[i]]} |")

# pré-entraîné vs de zéro
_, yb, pb = preds[best_pre["nom"]]; idz, yz, pz = preds[best_zero["nom"]]
out += [f"\n## Pré-entraîné ({best_pre['nom']}) vs de zéro ({best_zero['nom']})\n",
        "### Par classe (rappel / F1)\n", "| Classe | n | rappel pré-entraîné | rappel de zéro | F1 pré-entraîné | F1 de zéro |", "|---|---|---|---|---|---|"]
f1b = f1_score(yb, pb, labels=range(4), average=None, zero_division=0); f1z = f1_score(yz, pz, labels=range(4), average=None, zero_division=0)
for k in range(4):
    msk = yb == k
    out.append(f"| {ORDRE[k]} | {msk.sum()} | {np.mean(pb[msk] == k):.0%} | {np.mean(pz[msk] == k):.0%} | {f1b[k]:.2f} | {f1z[k]:.2f} |")
out += ["\n### Par type de texte (exactitude, erreur moyenne en classes)\n",
        "| Type | n | exact. pré-entraîné | exact. de zéro | écart moyen pré-entraîné | écart moyen de zéro |", "|---|---|---|---|---|---|"]
types = np.array([test[i]["type"] for i in idz])
for t in sorted(set(types), key=lambda t: -np.sum(types == t)):
    msk = types == t
    if msk.sum() < 5: continue
    out.append(f"| {t} | {msk.sum()} | {np.mean(pb[msk] == yb[msk]):.0%} | {np.mean(pz[msk] == yz[msk]):.0%} | "
               f"{np.mean(abs(pb[msk] - yb[msk])):.2f} | {np.mean(abs(pz[msk] - yz[msk])):.2f} |")
d_pre = np.sum((pb == yb) & (pz != yz)); d_zero = np.sum((pz == yz) & (pb != yb))
out.append(f"\nTextes bien classés par le pré-entraîné seulement : {d_pre} ; par le modèle de zéro seulement : {d_zero}.")

open("results/evaluation.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
