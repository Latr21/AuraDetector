"""Phase 2 : CamemBERT avec validation HORS DOMAINE (data/val_domaine.csv).

- Le choix du meilleur checkpoint (early stopping) se fait sur le kappa quadratique de val_domaine.
- Les sorties brutes (logits ou score) sont sauvegardées pour val_domaine ET pour le test, mais AUCUNE métrique
  n'est calculée sur le test ici : l'évaluation finale se fait une seule fois, dans scripts/phase2_final.py.

  python scripts/train_camembert_v2.py --mode regression --seed 42 --out models/p2_reg_s42
  python scripts/train_camembert_v2.py --class-weights --divine-weight 2 --out models/p2_cls_w2_s42
"""
import argparse, csv, json, os, random, shutil, sys, time

import numpy as np
import torch
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding,
                          EarlyStoppingCallback, Trainer, TrainingArguments)

sys.path.insert(0, os.path.dirname(__file__))
from commun import ORDRE, COURT, lire, metriques, score_vers_classe, afficher_matrice

TRAIN_P2 = ["data/train_synthetique.csv", "data/grok_textes.csv", "data/paires_contrastees.csv",
            "data/train_registres.csv", "data/train_battle.csv", "data/train_joutes_reelles.csv"]
if os.path.exists("data/punchlines_collectees.csv"): TRAIN_P2.append("data/punchlines_collectees.csv")


class DS(torch.utils.data.Dataset):
    def __init__(self, enc, y): self.enc, self.y = enc, y
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        d = {k: v[i] for k, v in self.enc.items()}; d["labels"] = self.y[i]; return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="+", default=TRAIN_P2)
    ap.add_argument("--val", default="data/val_domaine.csv")
    ap.add_argument("--test", default="data/test_reel.csv")
    ap.add_argument("--model", default="almanach/camembert-base")
    ap.add_argument("--mode", choices=["classification", "regression"], default="classification")
    ap.add_argument("--epochs", type=float, default=6)
    ap.add_argument("--patience", type=int, default=2)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--grad-accum", type=int, default=1)
    ap.add_argument("--grad-ckpt", action="store_true")
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--class-weights", action="store_true")
    ap.add_argument("--divine-weight", type=float, default=1.0, help="multiplie le poids de la classe Divine")
    ap.add_argument("--keep-v1-scores", action="store_true")
    ap.add_argument("--no-save", action="store_true", help="ne pas garder le modèle final (≈ 450 Mo base, 1,3 Go large)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    reg = a.mode == "regression"

    train, val = lire(a.train), lire([a.val])
    test = list(csv.DictReader(open(a.test, encoding="utf-8-sig")))
    interdits = {r["texte"] for r in val} | {r["texte"] for r in test}
    train = [r for r in train if r["texte"] not in interdits]
    if reg:
        train = [r for r in train if r.get("score", "").strip() != ""]
        if not a.keep_v1_scores: train = [r for r in train if r.get("origine") != "v1_poesie"]
    print(f"[{a.mode}] train {len(train)} | val_domaine {len(val)} | test {len(test)} (sorties brutes seulement)")

    tok = AutoTokenizer.from_pretrained(a.model)
    mkw = dict(num_labels=1, problem_type="regression") if reg else dict(
        num_labels=4, problem_type="single_label_classification",
        id2label=dict(enumerate(ORDRE)), label2id={c: i for i, c in enumerate(ORDRE)})
    model = AutoModelForSequenceClassification.from_pretrained(a.model, **mkw)
    if a.grad_ckpt: model.gradient_checkpointing_enable()

    cible = (lambda r: float(r["score"]) / 100.0) if reg else (lambda r: ORDRE.index(r["classe"]))
    def ds(rows, avec_cible=True):
        enc = tok([r["texte"] for r in rows], truncation=True, max_length=a.max_len)
        return DS(enc, [cible(r) if avec_cible else 0 for r in rows])
    def vers_classes(o):
        o = o[0] if isinstance(o, tuple) else o
        return [score_vers_classe(x * 100) for x in o.reshape(-1)] if reg else list(np.argmax(o, -1))
    yval = [ORDRE.index(r["classe"]) for r in val]
    def compute_metrics(ev):
        p = vers_classes(ev.predictions)
        return metriques(yval, p) if len(p) == len(yval) else {}   # jamais de métriques sur le test ici

    TrainerCls = Trainer
    if not reg and a.class_weights:
        cnt = np.bincount([ORDRE.index(r["classe"]) for r in train], minlength=4)
        w = len(train) / (4 * cnt); w[3] *= a.divine_weight
        w = torch.tensor(w, dtype=torch.float)
        print("Poids de classes :", dict(zip(COURT, w.round(decimals=3).tolist())))

        class WT(Trainer):
            def compute_loss(self, model, inputs, return_outputs=False, **kw):
                labels = inputs.pop("labels"); out = model(**inputs)
                loss = torch.nn.functional.cross_entropy(out.logits, labels, weight=w.to(out.logits.device))
                return (loss, out) if return_outputs else loss
        TrainerCls = WT

    kw = dict(output_dir=a.out, num_train_epochs=a.epochs, learning_rate=a.lr, per_device_train_batch_size=a.batch,
              per_device_eval_batch_size=a.batch * 2, gradient_accumulation_steps=a.grad_accum, weight_decay=0.01,
              warmup_steps=0.1, eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True,
              metric_for_best_model="kappa_quadratique", greater_is_better=True, save_total_limit=1,
              logging_steps=100, seed=a.seed, report_to="none", fp16=torch.cuda.is_available(), disable_tqdm=True)
    trainer = TrainerCls(model=model, args=TrainingArguments(**kw), train_dataset=ds(train), eval_dataset=ds(val),
                         data_collator=DataCollatorWithPadding(tok), compute_metrics=compute_metrics,
                         callbacks=[EarlyStoppingCallback(early_stopping_patience=a.patience)])
    t0 = time.time(); trainer.train(); duree = time.time() - t0

    hist = [l for l in trainer.state.log_history if "eval_kappa_quadratique" in l]
    best = max(hist, key=lambda l: l["eval_kappa_quadratique"])
    out_val = trainer.predict(ds(val)).predictions
    out_test = trainer.predict(ds(test, avec_cible=False)).predictions
    out_val = out_val[0] if isinstance(out_val, tuple) else out_val
    out_test = out_test[0] if isinstance(out_test, tuple) else out_test
    if reg: out_val, out_test = out_val.reshape(-1) * 100, out_test.reshape(-1) * 100
    np.save(os.path.join(a.out, "sorties_val.npy"), out_val); np.save(os.path.join(a.out, "sorties_test.npy"), out_test)
    pv = vers_classes(out_val / 100 if reg else out_val)
    res = dict(args=vars(a), mode=a.mode, temps_entrainement_s=duree, n_parametres=sum(p.numel() for p in model.parameters()),
               best_epoch=best["epoch"], historique_val=[{k: v for k, v in l.items() if k.startswith("eval_") or k == "epoch"} for l in hist],
               val_domaine=metriques(yval, pv), n_train=len(train))
    json.dump(res, open(os.path.join(a.out, "resultats.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False, default=float)
    print("\nval_domaine :", {k: round(v, 3) for k, v in res["val_domaine"].items()}, f"| meilleure epoch {best['epoch']} | {duree / 60:.1f} min")
    afficher_matrice(yval, pv)
    for d in os.listdir(a.out):   # checkpoints intermédiaires : on libère le disque
        if d.startswith("checkpoint"): shutil.rmtree(os.path.join(a.out, d), ignore_errors=True)
    if not a.no_save:
        trainer.save_model(os.path.join(a.out, "final")); tok.save_pretrained(os.path.join(a.out, "final"))


if __name__ == "__main__":
    main()
