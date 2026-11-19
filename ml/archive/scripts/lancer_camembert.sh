#!/bin/sh
# Lance les 3 entraînements CamemBERT (depuis ml/)
export PYTHONIOENCODING=utf-8 TQDM_DISABLE=1
T="data/train_synthetique.csv data/grok_textes.csv data/paires_contrastees.csv"
P=.venv/Scripts/python
$P scripts/train_camembert.py --train $T --out models/camembert_classif > results/camembert_classif.log 2>&1
$P scripts/train_camembert.py --train $T --mode regression --out models/camembert_regression > results/camembert_regression.log 2>&1
$P scripts/train_camembert.py --train $T --class-weights --out models/camembert_classif_pondere > results/camembert_classif_pondere.log 2>&1
