#!/bin/sh
# Recherche du taux d'apprentissage de CamemBERT (régression, base, graine 42) — 3e-5 existe déjà (p2_reg_s42)
export PYTHONIOENCODING=utf-8
for lr in 2e-5 5e-5; do
  .venv/Scripts/python scripts/train_camembert_v2.py --mode regression --lr $lr --seed 42 --out models/p2_reg_lr${lr}_s42 > results/p2_reg_lr${lr}_s42.log 2>&1
done
