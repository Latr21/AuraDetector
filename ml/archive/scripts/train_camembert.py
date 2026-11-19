"""Fine-tuning de CamemBERT pour Aura Classifier.

Exemples :
  python scripts/train_camembert.py                                   # classification, données par défaut
  python scripts/train_camembert.py --mode regression                 # prédit le score, puis en déduit la classe
  python scripts/train_camembert.py --train data/train_synthetique.csv data/textes_amis_annotes.csv

Chaque fichier d'entraînement doit avoir au moins les colonnes `texte` et `classe` (et `score` en mode régression).
Le jeu de test (`--test`) n'est JAMAIS utilisé pour l'entraînement ni pour choisir le meilleur modèle.
"""
import argparse, csv, inspect, json, os, random, time

import numpy as np
import torch
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding,
                          Trainer, TrainingArguments)

ORDRE = ["Anti-Aura", "Aura Correcte", "Forte Aura", "Aura Divine"]
SEUILS = [(-100, -11), (-10, 24), (25, 74), (75, 100)]
COURT = ["Anti", "Corr", "Fort", "Divi"]


def score_vers_classe(s):
    s = int(round(max(-100, min(100, s))))
    return next(i for i, (a, b) in enumerate(SEUILS) if a <= s <= b)


def lire(chemins):
    rows = []
    for p in chemins:
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            if r.get("texte", "").strip() and r.get("classe", "").strip() in ORDRE:
                r["_fichier"] = os.path.basename(p)
                rows.append(r)
    return rows


class DS(torch.utils.data.Dataset):
    def __init__(self, enc, y): self.enc, self.y = enc, y
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        d = {k: v[i] for k, v in self.enc.items()}
        d["labels"] = self.y[i]
        return d


def metriques(y, p):
    return dict(accuracy=accuracy_score(y, p), a_une_classe_pres=float(np.mean(np.abs(np.array(y) - np.array(p)) <= 1)),
                f1_macro=f1_score(y, p, average="macro", labels=list(range(4)), zero_division=0),
                kappa_quadratique=cohen_kappa_score(y, p, weights="quadratic", labels=list(range(4))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="+", default=["data/train_synthetique.csv"])
    ap.add_argument("--test", default="data/test_reel.csv")
    ap.add_argument("--model", default="almanach/camembert-base")
    ap.add_argument("--mode", choices=["classification", "regression"], default="classification")
    ap.add_argument("--epochs", type=float, default=4)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--val-frac", type=float, default=0.1)
    ap.add_argument("--keep-v1-scores", action="store_true",
                    help="En régression, garder les scores de la v1 (calculés avec l'ancienne formule). Exclus par défaut.")
    ap.add_argument("--class-weights", action="store_true",
                    help="Classification : pondère l'entropie croisée par l'inverse de la fréquence des classes (train).")
    ap.add_argument("--out", default="modele_aura")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    train = lire(a.train)
    if a.mode == "regression":
        train = [r for r in train if r.get("score", "").strip() != ""]
        if not a.keep_v1_scores:
            avant = len(train)
            train = [r for r in train if r.get("origine") != "v1_poesie"]
            print(f"Régression : {avant - len(train)} lignes v1 exclues (ancienne formule). --keep-v1-scores pour les garder.")
    test = lire([a.test]) if a.test and os.path.exists(a.test) else []
    test_txt = {r["texte"] for r in test}
    fuite = [r for r in train if r["texte"] in test_txt]
    if fuite:
        print(f"Attention : {len(fuite)} textes du test étaient dans le train, ils sont retirés du train.")
        train = [r for r in train if r["texte"] not in test_txt]
    print(f"Train : {len(train)} textes ({', '.join(sorted({r['_fichier'] for r in train}))}) | Test réel : {len(test)}")

    y_cls = [ORDRE.index(r["classe"]) for r in train]
    tr, va = train_test_split(train, test_size=a.val_frac, stratify=y_cls, random_state=a.seed)

    tok = AutoTokenizer.from_pretrained(a.model)
    reg = a.mode == "regression"
    mkw = dict(num_labels=1, problem_type="regression") if reg else dict(
        num_labels=4, problem_type="single_label_classification",
        id2label=dict(enumerate(ORDRE)), label2id={c: i for i, c in enumerate(ORDRE)})
    model = AutoModelForSequenceClassification.from_pretrained(a.model, **mkw)

    def cible(r): return float(r["score"]) / 100.0 if reg else ORDRE.index(r["classe"])
    def ds(rows):
        enc = tok([r["texte"] for r in rows], truncation=True, max_length=a.max_len)
        return DS(enc, [cible(r) for r in rows])

    def vers_classes(pred):
        logits = pred[0] if isinstance(pred, tuple) else pred
        return [score_vers_classe(x * 100) for x in logits.reshape(-1)] if reg else list(np.argmax(logits, -1))

    def compute_metrics(ev):
        y = [score_vers_classe(v * 100) for v in ev.label_ids.reshape(-1)] if reg else list(ev.label_ids)
        return metriques(y, vers_classes(ev.predictions))

    kw = dict(output_dir=a.out, num_train_epochs=a.epochs, learning_rate=a.lr, per_device_train_batch_size=a.batch,
              per_device_eval_batch_size=a.batch * 2, weight_decay=0.01, save_strategy="epoch",
              load_best_model_at_end=True, metric_for_best_model="kappa_quadratique", greater_is_better=True,
              save_total_limit=1, logging_steps=50, seed=a.seed, report_to="none",
              fp16=torch.cuda.is_available())
    params = inspect.signature(TrainingArguments.__init__).parameters
    # transformers >= 5 : warmup_ratio supprimé, warmup_steps accepte une fraction
    kw["warmup_ratio" if "warmup_ratio" in params else "warmup_steps"] = 0.1
    strat = "eval_strategy" if "eval_strategy" in inspect.signature(TrainingArguments.__init__).parameters else "evaluation_strategy"
    kw[strat] = "epoch"
    TrainerCls = Trainer
    if a.class_weights and not reg:
        cnt = np.bincount([ORDRE.index(r["classe"]) for r in tr], minlength=4)
        w = torch.tensor(len(tr) / (4 * cnt), dtype=torch.float)
        print("Poids de classes :", dict(zip(COURT, w.round(decimals=3).tolist())))

        class WeightedTrainer(Trainer):
            def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
                labels = inputs.pop("labels")
                out = model(**inputs)
                loss = torch.nn.functional.cross_entropy(out.logits, labels, weight=w.to(out.logits.device))
                return (loss, out) if return_outputs else loss
        TrainerCls = WeightedTrainer
    t0 = time.time()
    trainer = TrainerCls(model=model, args=TrainingArguments(**kw), train_dataset=ds(tr), eval_dataset=ds(va),
                      data_collator=DataCollatorWithPadding(tok), compute_metrics=compute_metrics)
    trainer.train()
    duree = time.time() - t0

    res = {"validation_synthetique": {k.replace("eval_", ""): v for k, v in trainer.evaluate().items()
                                      if k.startswith("eval_") and not k.endswith(("runtime", "per_second"))}}
    res["temps_entrainement_s"] = duree
    res["n_parametres"] = sum(p.numel() for p in model.parameters())
    if test:
        pred = trainer.predict(ds(test))
        p = vers_classes(pred.predictions); y = [ORDRE.index(r["classe"]) for r in test]
        res["test_reel"] = metriques(y, p)
        print("\nMatrice test réel (lignes = référence)")
        print("      " + " ".join(f"{c:>5}" for c in COURT))
        for c, row in zip(COURT, confusion_matrix(y, p, labels=list(range(4)))):
            print(f"{c:>5} " + " ".join(f"{v:>5}" for v in row))
        with open(os.path.join(a.out, "predictions_test_reel.csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(["id", "texte", "classe_reference", "prediction"])
            for r, k in zip(test, p): w.writerow([r.get("id", ""), r["texte"], r["classe"], ORDRE[k]])

    trainer.save_model(os.path.join(a.out, "final")); tok.save_pretrained(os.path.join(a.out, "final"))
    json.dump(res, open(os.path.join(a.out, "resultats.json"), "w"), indent=2, ensure_ascii=False, default=float)
    print("\n" + json.dumps(res, indent=2, ensure_ascii=False, default=float))
    print(f"\nModèle sauvegardé dans {a.out}/final")


if __name__ == "__main__":
    main()
