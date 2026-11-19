#!/bin/sh
# Phase 2, bloc B (depuis ml/) : graines supplémentaires de la meilleure classification (poids Divine x3, choisi sur val_domaine)
# puis camembert-large en régression (fp16, batch 4 x accumulation 4, gradient checkpointing : pic 6,7 Go)
export PYTHONIOENCODING=utf-8
P=.venv/Scripts/python
for s in 43 44; do
  $P scripts/train_camembert_v2.py --class-weights --divine-weight 3 --seed $s --out models/p2_cls_w3_s$s > results/p2_cls_w3_s$s.log 2>&1
done
$P scripts/train_camembert_v2.py --model almanach/camembert-large --mode regression --epochs 4 --batch 4 --grad-accum 4 --grad-ckpt --lr 1.5e-5 --seed 42 --out models/p2_large_reg_s42 > results/p2_large_reg_s42.log 2>&1
