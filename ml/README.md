# Aura Classifier — kit d'entraînement

## Contenu

| Fichier | Rôle |
| --- | --- |
| `data/train_synthetique.csv` | 6 991 textes générés (≈2 000 Anti, 2 000 Correcte, 2 000 Forte, 1 000 Divine) : v1 poésie (1 400), v3 argot internet/politique (699), v4 registres variés (4 892 : hémicycle, réponses ministérielles, procédure, textes juridiques, maximes, fables, bios, messages de nuit, argot internet) |
| `data/test_reel.csv` | 330 vrais textes pré-annotés par une IA : Assemblée nationale, littérature et théâtre du domaine public (Cyrano, Madame Bovary, Hugo…), citations publiques de personnalités politiques de plusieurs bords (Wikiquote et sites de citations), conférences de presse sportives, tweets de marques, textes officiels. Colonne `source` = lien. **Jamais pour l'entraînement** |
| `data/test_annotateur_vierge.csv` | Les mêmes 330 textes sans étiquette, pour un annotateur humain |
| `data/grok_textes.csv` | 105 textes écrits par Grok, étiquettes revues par une seconde IA (28 corrigées ; colonnes `classe_grok`/`score_grok` = notes d'origine). Entraînement uniquement |
| `data/annotation_grok_lot1.csv` | Notes de Grok sur 82 textes du test (2e annotateur, lot 1) |
| `data/kit_collecte_textes.csv` | Modèle de fichier à envoyer à des amis pour collecter de vrais textes |
| `PROMPT_PROJET.md` | Consignes de la suite du projet (paires contrastées, CamemBERT, évaluation) |
| `scripts/tester_baseline.py` | Teste le modèle de base sur des phrases libres : `python scripts/tester_baseline.py "ta phrase"` |
| `scripts/baseline.py` | Modèle de base rapide (TF-IDF + régression logistique), tourne sur CPU en 1 min |
| `scripts/train_camembert.py` | Fine-tuning CamemBERT (classification ou régression du score) |
| `scripts/predire.py` | Prédire l'Aura de nouveaux textes avec le modèle entraîné |
| `scripts/accord.py` | Accord entre deux annotateurs (kappa pondéré, désaccords) |
| `scripts/generateurs/` | Scripts qui ont produit les données synthétiques (pour en régénérer ou en modifier) |

Formule actuelle (sans Mystère) : `Aura = 0,333 R + 0,222 S + 0,167 O + 0,167 B + 0,111 P`.

Quatre classes (la colonne `classe_7` garde l'ancienne étiquette à 7 classes) :

| Classe | Score | Ancien regroupement |
| --- | --- | --- |
| Anti-Aura | -100 à -11 | Anti-Aura + Faible |
| Aura Correcte | -10 à +24 | Neutre + Correcte |
| Forte Aura | +25 à +74 | Forte + Légendaire |
| Aura Divine | +75 à +100 | Divine |

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Un GPU est fortement conseillé pour CamemBERT (Google Colab gratuit suffit). Sur CPU, compter plusieurs heures.

## Modèles CamemBERT (Hugging Face)

L'ensemble CamemBERT retenu (4 modèles, ≈2,6 Go) est trop gros pour GitHub : il est hébergé sur le
Hugging Face Hub (dépôt indiqué dans `hf_repo.txt`). Au démarrage, l'API le télécharge automatiquement
dans `models/` s'il manque. Pour le faire à la main :

```bash
python scripts/hf_modeles.py telecharger
```

Pour publier de nouveaux modèles (compte HF requis) :

```bash
hf auth login                              # token avec droit d'écriture : huggingface.co/settings/tokens
python scripts/hf_modeles.py envoyer       # crée <utilisateur>/aura-detector-camembert et écrit hf_repo.txt
```

## Lancer

Tous les scripts se lancent depuis la racine du dossier.

```bash
python scripts/baseline.py                               # référence rapide
python scripts/train_camembert.py                        # CamemBERT, classification 4 classes
python scripts/train_camembert.py --mode regression      # CamemBERT, prédit le score puis la classe
python scripts/predire.py "Le chaos, c'est vous !"
```

Ajouter des données (textes d'amis notés, vrais textes annotés) : il suffit de les lister après `--train`.
Colonnes requises : `texte`, `classe` (et `score` pour la régression).

```bash
python scripts/train_camembert.py --train data/train_synthetique.csv data/textes_amis_annotes.csv
```

Résultats dans `modele_aura/` : `resultats.json`, `predictions_test_reel.csv`, et le modèle dans `final/`.

## Lire les résultats

Regarder **le test réel**, pas la validation : la validation est tirée des données synthétiques et sera toujours flatteuse.

Référence actuelle (modèle de base, 4 classes, test de 330 textes) : kappa 0,05 en classification et 0,15 en régression du score. Répondre toujours « Aura Correcte » fait déjà 58 % de bonnes réponses : regardez le kappa, le F1-macro et la matrice de confusion, pas le pourcentage.

Indicateur principal : le **kappa quadratique**. Il vaut 0 pour un modèle qui répond toujours la même chose et 1 pour un modèle parfait, et il pénalise davantage les grosses erreurs (Anti-Aura prédit Divine).

## À savoir

- Aucun texte synthétique ne partage de séquence de 6 mots avec le test réel (vérifié et filtré).
- Les scores de la v1 utilisent l'ancienne formule. En mode régression, ces lignes sont exclues par défaut (`--keep-v1-scores` pour les garder). Leurs classes restent valables.
- Le test réel reste déséquilibré : 191 Aura Correcte, 65 Forte, 41 Anti-Aura, 33 Divine. Les classes rares y sont mal mesurées tant que vous n'aurez pas ajouté de vrais textes.
- Aura Divine a moitié moins d'exemples d'entraînement : le modèle de base compense avec `class_weight="balanced"`.
- Les extraits littéraires et les textes de loi du test ont été cités de mémoire : à vérifier sur Wikisource et Légifrance avant de figer le test.
- Les étiquettes du test réel viennent d'un seul annotateur (une IA). Faites remplir `test_annotateur_vierge.csv` par un humain, puis :
  `python scripts/accord.py data/test_reel.csv son_fichier.csv`
