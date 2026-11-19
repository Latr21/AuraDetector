#!/bin/sh
# Phase 2, bloc A (depuis ml/) : régression x3 graines, classification poids Divine x1/x2/x3
export PYTHONIOENCODING=utf-8
P=.venv/Scripts/python
for s in 42 43 44; do
  $P scripts/train_camembert_v2.py --mode regression --seed $s --out models/p2_reg_s$s > results/p2_reg_s$s.log 2>&1
done
for w in 1 2 3; do
  $P scripts/train_camembert_v2.py --class-weights --divine-weight $w --seed 42 --out models/p2_cls_w${w}_s42 > results/p2_cls_w${w}_s42.log 2>&1
done
