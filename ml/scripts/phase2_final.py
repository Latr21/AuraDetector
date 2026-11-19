"""Phase 2 : choix (val_domaine seulement) puis évaluation finale unique sur le test réel.

  python scripts/phase2_final.py choisir    # seuils, ensembles, poids : tout est choisi sur data/val_domaine.csv
  python scripts/phase2_final.py evaluer    # applique les choix au test réel (une seule fois) et écrit results/phase2.md

Représentation commune : chaque modèle produit un « score continu » s sur l'échelle officielle (-100..100).
  - régression : s = score prédit ;
  - classification : s = Σ_k p_k · centre_k (centres -55, 7, 50, 87).
Les seuils (t1, t2, t3) qui transforment s en classe sont optimisés sur val_domaine pour maximiser le kappa quadratique.
"""
import csv, glob, itertools, json, os, sys

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import confusion_matrix, recall_score
from sklearn.pipeline import make_pipeline, make_union

sys.path.insert(0, os.path.dirname(__file__))
from commun import ORDRE, COURT, lire, metriques, score_vers_classe

CENTRES = np.array([-55.0, 7.0, 50.0, 87.0])
SEUILS_OFFICIELS = (-10.5, 24.5, 74.5)
VAL, TEST = "data/val_domaine.csv", "data/test_reel.csv"
TRAIN_P2 = ["data/train_synthetique.csv", "data/grok_textes.csv", "data/paires_contrastees.csv",
            "data/train_registres.csv", "data/train_battle.csv", "data/train_joutes_reelles.csv"]


def qwk(y, p, k=4):
    O = np.zeros((k, k)); np.add.at(O, (y, p), 1)
    W = (np.subtract.outer(np.arange(k), np.arange(k)) ** 2) / (k - 1) ** 2
    E = np.outer(O.sum(1), O.sum(0)) / O.sum()
    return 1 - (W * O).sum() / max((W * E).sum(), 1e-9)


def classer(s, t): return np.digitize(s, t)


def optimiser_seuils(s, y):
    """Recherche par grille (pas de 2) puis affinage (pas de 0,5) des seuils t1 < t2 < t3."""
    best = (qwk(y, classer(s, SEUILS_OFFICIELS)), SEUILS_OFFICIELS)
    for t1, t2, t3 in itertools.product(range(-50, 21, 2), range(-10, 61, 2), range(20, 91, 2)):
        if t1 < t2 < t3:
            k = qwk(y, classer(s, (t1, t2, t3)))
            if k > best[0] + 1e-9: best = (k, (t1, t2, t3))
    t = list(best[1])
    for _ in range(2):
        for i in range(3):
            for d in np.arange(-3, 3.01, 0.5):
                c = t.copy(); c[i] += d
                if c[0] < c[1] < c[2]:
                    k = qwk(y, classer(s, c))
                    if k > best[0] + 1e-9: best = (k, tuple(c)); t = c
    return best[1], best[0]


def score_continu(sorties, mode):
    if mode == "regression": return np.asarray(sorties, dtype=float).reshape(-1)
    z = sorties - sorties.max(1, keepdims=True); p = np.exp(z); p /= p.sum(1, keepdims=True)
    return p @ CENTRES


def charger_runs():
    runs = {}
    for d in sorted(glob.glob("models/p2_*")):
        f = os.path.join(d, "resultats.json")
        if not os.path.exists(f) or not os.path.exists(os.path.join(d, "sorties_val.npy")): continue
        r = json.load(open(f, encoding="utf-8"))
        bv, bt = np.load(os.path.join(d, "sorties_val.npy")), np.load(os.path.join(d, "sorties_test.npy"))
        runs[os.path.basename(d)] = dict(mode=r["mode"], res=r, dossier=d,
                                         argmax_val=bv.argmax(1) if r["mode"] != "regression" else None,
                                         argmax_test=bt.argmax(1) if r["mode"] != "regression" else None,
                                         val=score_continu(np.load(os.path.join(d, "sorties_val.npy")), r["mode"]),
                                         test=score_continu(np.load(os.path.join(d, "sorties_test.npy")), r["mode"]))
    return runs


def baseline_tfidf():
    """Baseline TF-IDF (phase 1) réentraînée sur les données de la phase 2 : sorties val et test."""
    tr = [r for r in lire(TRAIN_P2)]
    val, test = lire([VAL]), list(csv.DictReader(open(TEST, encoding="utf-8-sig")))
    feats = lambda: make_union(TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True),
                               TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True))
    X = [r["texte"] for r in tr]
    clf = make_pipeline(feats(), LogisticRegression(max_iter=3000, C=4, class_weight="balanced")).fit(X, [ORDRE.index(r["classe"]) for r in tr])
    import joblib; joblib.dump(clf, "models/p2_tfidf.joblib")   # réutilisé par l'API si l'ensemble l'inclut
    out = {}
    for nom, rows in (("val", val), ("test", test)):
        out[nom] = clf.predict_proba([r["texte"] for r in rows]) @ CENTRES
    return out


def choisir():
    yv = np.array([ORDRE.index(r["classe"]) for r in lire([VAL])])
    runs = charger_runs()
    print(f"{len(runs)} runs CamemBERT phase 2 trouvés")
    cands = {}
    for nom, r in runs.items():   # modèles seuls : seuils officiels et seuils optimisés
        p0 = r["argmax_val"] if r["mode"] != "regression" else classer(r["val"], SEUILS_OFFICIELS)
        cands[nom] = dict(composants={nom: 1.0}, seuils=SEUILS_OFFICIELS, val_kappa=qwk(yv, p0), argmax=r["mode"] != "regression")
        t, k = optimiser_seuils(r["val"], yv)
        cands[nom + "+seuils"] = dict(composants={nom: 1.0}, seuils=t, val_kappa=k)
    # ensembles par graines (même configuration, graines différentes)
    groupes = {}
    for nom in runs: groupes.setdefault(nom.rsplit("_s", 1)[0], []).append(nom)
    for g, noms in groupes.items():
        if len(noms) > 1:
            s = np.mean([runs[n]["val"] for n in noms], 0); t, k = optimiser_seuils(s, yv)
            cands[f"{g}_ens{len(noms)}+seuils"] = dict(composants={n: 1 / len(noms) for n in noms}, seuils=t, val_kappa=k)
    # ensemble combiné : régression (graines) + classification (meilleur groupe) + baseline TF-IDF ; poids sur val
    tf = baseline_tfidf(); json.dump({k: v.tolist() for k, v in tf.items()}, open("results/p2_tfidf_sorties.json", "w"))
    reg = [g for g in groupes if runs[groupes[g][0]]["mode"] == "regression"]
    cls = [g for g in groupes if runs[groupes[g][0]]["mode"] != "regression"]
    def ens_val(g): return np.mean([runs[n]["val"] for n in groupes[g]], 0)
    if reg and cls:
        g_cls = max(cls, key=lambda g: optimiser_seuils(ens_val(g), yv)[1])
        g_reg = max(reg, key=lambda g: optimiser_seuils(ens_val(g), yv)[1])
        sr, sc = ens_val(g_reg), ens_val(g_cls)
        best = None
        for wr in np.arange(0, 1.01, 0.1):
            for wt in np.arange(0, 1.01 - wr, 0.1):
                wc = 1 - wr - wt
                s = wr * sr + wc * sc + wt * tf["val"]; t, k = optimiser_seuils(s, yv)
                if best is None or k > best[0] + 1e-9: best = (k, wr, wc, wt, t)
        k, wr, wc, wt, t = best
        comp = {n: wr / len(groupes[g_reg]) for n in groupes[g_reg]}
        comp.update({n: wc / len(groupes[g_cls]) for n in groupes[g_cls]}); comp["tfidf"] = wt
        cands["ensemble_combine"] = dict(composants={c: float(v) for c, v in comp.items() if v > 0}, seuils=t, val_kappa=k,
                                         poids=dict(regression=float(wr), classification=float(wc), tfidf=float(wt), groupe_reg=g_reg, groupe_cls=g_cls))
    meilleur = max(cands, key=lambda c: cands[c]["val_kappa"])
    meilleur_simple = max([c for c in cands if c in runs or c.endswith("+seuils") and c[:-7] in runs], key=lambda c: cands[c]["val_kappa"])
    json.dump(dict(candidats=cands, meilleur=meilleur, meilleur_simple=meilleur_simple), open("results/p2_choix.json", "w", encoding="utf-8"),
              indent=2, ensure_ascii=False, default=float)
    print("\n| Candidat (choix sur val_domaine) | seuils | kappa val_domaine |\n|---|---|---|")
    for c, v in sorted(cands.items(), key=lambda x: -x[1]["val_kappa"]):
        print(f"| {c} | {tuple(round(float(x), 1) for x in v['seuils'])} | {v['val_kappa']:.3f} |")
    print(f"\nMeilleur sur val_domaine : {meilleur} ; meilleur modèle seul : {meilleur_simple}")


def evaluer():
    choix = json.load(open("results/p2_choix.json", encoding="utf-8"))
    runs = charger_runs(); tf = {k: np.array(v) for k, v in json.load(open("results/p2_tfidf_sorties.json")).items()}
    test = list(csv.DictReader(open(TEST, encoding="utf-8-sig"))); yt = np.array([ORDRE.index(r["classe"]) for r in test])
    vald = lire([VAL]); yv = np.array([ORDRE.index(r["classe"]) for r in vald])
    def sortie(cand, part):
        return sum(w * (tf[part] if n == "tfidf" else runs[n][part]) for n, w in cand["composants"].items())
    retenus = [c for c in choix["candidats"] if not c.endswith("+seuils") or True]
    lignes, preds = [], {}
    for c in retenus:
        cand = choix["candidats"][c]
        p = runs[c]["argmax_test"] if cand.get("argmax") else classer(sortie(cand, "test"), cand["seuils"]); preds[c] = p
        m = metriques(yt, p); rec = recall_score(yt, p, labels=range(4), average=None, zero_division=0)
        lignes.append((c, cand["val_kappa"], m, rec))
    out = ["## Phase 2 — évaluation finale unique sur le test réel (330 textes)\n",
           "| Modèle | kappa val_domaine | Exactitude | ±1 | F1-macro | **Kappa test** | Rappel Anti | Rappel Corr | Rappel Forte | Rappel Divine |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for c, kv, m, rec in sorted(lignes, key=lambda x: -x[1]):
        out.append(f"| {c} | {kv:.3f} | {m['accuracy']:.1%} | {m['a_une_classe_pres']:.1%} | {m['f1_macro']:.2f} | **{m['kappa_quadratique']:.3f}** | "
                   + " | ".join(f"{r:.0%}" for r in rec) + " |")
    best = choix["meilleur"]; pb = preds[best]
    out += [f"\nModèle retenu (meilleur kappa sur val_domaine, choisi AVANT de regarder le test) : **{best}**",
            f"composants : {choix['candidats'][best]['composants']} ; seuils : {tuple(round(float(x), 1) for x in choix['candidats'][best]['seuils'])}\n",
            "### Matrice de confusion (test réel)\n", "| réf. \\ prédit | " + " | ".join(COURT) + " |", "|---|---|---|---|---|"]
    out += [f"| **{c}** | " + " | ".join(str(v) for v in row) + " |" for c, row in zip(COURT, confusion_matrix(yt, pb, labels=range(4)))]
    sb = sortie(choix["candidats"][best], "test")
    ordre = sorted(range(len(test)), key=lambda i: (-abs(int(yt[i]) - int(pb[i])), -abs(sb[i] - CENTRES[yt[i]])))[:15]
    out += ["\n### 15 pires erreurs (test réel)\n", "| id | type | texte | référence | prédiction (score) |", "|---|---|---|---|---|"]
    for i in ordre:
        t = test[i]["texte"].replace("|", "/").replace("\n", " ")
        out.append(f"| {test[i]['id']} | {test[i]['type']} | {t[:150]}{'…' if len(t) > 150 else ''} | {ORDRE[yt[i]]} | {ORDRE[pb[i]]} ({sb[i]:+.0f}) |")
    # avant / après par type : phase 1 = CamemBERT régression (phase 1)
    p1 = {r["id"]: ORDRE.index(r["prediction"]) for r in csv.DictReader(open("results/predictions_camembert_regression.csv", encoding="utf-8-sig"))}
    pa = np.array([p1[r["id"]] for r in test]); types = np.array([r["type"] for r in test])
    out += ["\n### Par type de texte : avant (CamemBERT régression, phase 1) / après (" + best + ")\n",
            "| Type | n | exact. avant | exact. après | écart moyen avant | écart moyen après |", "|---|---|---|---|---|---|"]
    for t in sorted(set(types), key=lambda t: -np.sum(types == t)):
        m = types == t
        if m.sum() < 5: continue
        out.append(f"| {t} | {m.sum()} | {np.mean(pa[m] == yt[m]):.0%} | {np.mean(pb[m] == yt[m]):.0%} | {np.mean(abs(pa[m] - yt[m])):.2f} | {np.mean(abs(pb[m] - yt[m])):.2f} |")
    ma = metriques(yt, pa); mb = metriques(yt, pb)
    out.append(f"\nGlobal : kappa {ma['kappa_quadratique']:.3f} → {mb['kappa_quadratique']:.3f} ; F1-macro {ma['f1_macro']:.2f} → {mb['f1_macro']:.2f}")
    # battle : validation uniquement (le test n'a pas de battle)
    sv = sortie(choix["candidats"][best], "val")
    pv = runs[best]["argmax_val"] if choix["candidats"][best].get("argmax") else classer(sv, choix["candidats"][best]["seuils"])
    mb_ = np.array([r.get("type") == "battle" for r in vald])
    out += ["\n### Registre battle (val_domaine, 40 textes)\n", "| réf. \\ prédit | " + " | ".join(COURT) + " |", "|---|---|---|---|---|"]
    out += [f"| **{c}** | " + " | ".join(str(v) for v in row) + " |" for c, row in zip(COURT, confusion_matrix(yv[mb_], pv[mb_], labels=range(4)))]
    spi = mb_ & (yv >= 2)
    out.append(f"\nClashs spirituels (Forte/Divine) prédits Forte ou Divine : {np.mean(pv[spi] >= 2):.0%} ({np.sum(pv[spi] >= 2)}/{spi.sum()}) ; "
               f"prédits Anti : {np.sum(pv[spi] == 0)}. Anti prédits Anti : {np.sum(pv[mb_ & (yv == 0)] == 0)}/{np.sum(mb_ & (yv == 0))}.")
    with open("results/predictions_phase2.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["id", "texte", "classe_reference", "prediction", "score_continu"])
        for r, k, s in zip(test, pb, sb): w.writerow([r["id"], r["texte"], r["classe"], ORDRE[k], f"{s:.1f}"])
    open("results/phase2.md", "w", encoding="utf-8").write("\n".join(out) + "\n"); print("\n".join(out))


if __name__ == "__main__":
    {"choisir": choisir, "evaluer": evaluer}[sys.argv[1]]()
