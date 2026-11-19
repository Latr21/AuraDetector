## Tableau comparatif (test réel, 330 textes)

| Modèle | Exactitude | ±1 classe | F1-macro | Kappa quadratique | Temps d'entraînement | Paramètres |
|---|---|---|---|---|---|---|
| Toujours « Aura Correcte » | 57.9 % | 90.0 % | 0.18 | 0.00 | – | – |
| Baseline TF-IDF+LR (synthétique seul) | 43.9% | 86.7% | 0.31 | **0.046** | 3 s | 128 060 |
| Baseline régression Ridge (synthétique seul) | 51.8% | 89.7% | 0.31 | **0.155** | 2 s | 32 015 |
| Baseline + Grok + paires (classif) | 38.2% | 84.2% | 0.32 | **0.172** | 4 s | 153 396 |
| Baseline + Grok + paires (régression) | 50.6% | 89.1% | 0.31 | **0.166** | 2 s | 38 349 |
| CamemBERT classification | 51.2% | 88.8% | 0.40 | **0.265** | 10.4 min | 110 625 028 |
| CamemBERT classification pondérée | 51.2% | 88.5% | 0.42 | **0.278** | 6.3 min | 110 625 028 |
| CamemBERT régression | 47.9% | 91.2% | 0.34 | **0.323** | 5.9 min | 110 622 721 |
| MLP NumPy (de zéro) | 40.0% | 84.8% | 0.33 | **0.178** | 4.3 min | 5 153 668 |
| BiLSTM classification (de zéro) | 43.6% | 83.3% | 0.34 | **0.215** | 2.3 min | 735 876 |
| BiLSTM régression (de zéro) | 50.9% | 88.8% | 0.35 | **0.196** | 2.3 min | 668 033 |

## Matrice de confusion du meilleur modèle : CamemBERT régression

| réf. \ prédit | Anti | Corr | Fort | Divi |
|---|---|---|---|---|
| **Anti** | 24 | 11 | 6 | 0 |
| **Corr** | 58 | 114 | 19 | 0 |
| **Fort** | 12 | 33 | 18 | 2 |
| **Divi** | 7 | 4 | 20 | 2 |

## Matrice de confusion du meilleur modèle entraîné de zéro : BiLSTM classification (de zéro)

| réf. \ prédit | Anti | Corr | Fort | Divi |
|---|---|---|---|---|
| **Anti** | 21 | 16 | 1 | 3 |
| **Corr** | 57 | 103 | 13 | 18 |
| **Fort** | 15 | 30 | 7 | 13 |
| **Divi** | 13 | 5 | 2 | 13 |

## 15 pires erreurs (CamemBERT régression)

| id | type | texte | référence | prédiction |
|---|---|---|---|---|
| T210 | poésie | Je suis belle, ô mortels ! comme un rêve de pierre, | Aura Divine | Anti-Aura |
| T211 | poésie | La chair est triste, hélas ! et j'ai lu tous les livres. | Aura Divine | Anti-Aura |
| T227 | prose | Parce que c'était lui, parce que c'était moi. | Aura Divine | Anti-Aura |
| T228 | théâtre | Bon appétit, messieurs ! — Ô ministres intègres ! Conseillers vertueux ! voilà votre façon De servir, serviteurs qui pillez la maison ! | Aura Divine | Anti-Aura |
| T229 | discours | De l'audace, encore de l'audace, toujours de l'audace, et la France est sauvée ! | Aura Divine | Anti-Aura |
| T257 | théâtre | Ah ?… Et moi, Cyrano-Savinien-Hercule De Bergerac. | Aura Divine | Anti-Aura |
| T284 | poésie | Nais, grandis, rêve, souffre, aime, vis, vieillis, tombe. | Aura Divine | Anti-Aura |
| T101 | discours | Aujourd’hui, le trouble de l’État, c’est vous. | Forte Aura | Anti-Aura |
| T162 | discours | Le chaos, c’est vous ! L’irresponsabilité, c’est vous ! La chienlit, c’est vous ! | Forte Aura | Anti-Aura |
| T213 | poésie | Il pleure dans mon cœur Comme il pleut sur la ville ; | Forte Aura | Anti-Aura |
| T219 | poésie | Waterloo ! Waterloo ! Waterloo ! morne plaine ! | Forte Aura | Anti-Aura |
| T222 | théâtre | Franchement, il est bon à mettre au cabinet. | Forte Aura | Anti-Aura |
| T223 | théâtre | C'est un roc !… c'est un pic !… c'est un cap ! Que dis-je, c'est un cap ?… C'est une péninsule ! | Aura Divine | Aura Correcte |
| T234 | fable | Le Corbeau, honteux et confus, Jura, mais un peu tard, qu'on ne l'y prendrait plus. | Anti-Aura | Forte Aura |
| T238 | théâtre | Votre prudence est endormie, De traiter magnifiquement Et de loger superbement Votre plus cruelle ennemie. | Anti-Aura | Forte Aura |

## Pré-entraîné (CamemBERT régression) vs de zéro (BiLSTM classification (de zéro))

### Par classe (rappel / F1)

| Classe | n | rappel pré-entraîné | rappel de zéro | F1 pré-entraîné | F1 de zéro |
|---|---|---|---|---|---|
| Anti-Aura | 41 | 59% | 51% | 0.34 | 0.29 |
| Aura Correcte | 191 | 60% | 54% | 0.65 | 0.60 |
| Forte Aura | 65 | 28% | 11% | 0.28 | 0.16 |
| Aura Divine | 33 | 6% | 39% | 0.11 | 0.33 |

### Par type de texte (exactitude, erreur moyenne en classes)

| Type | n | exact. pré-entraîné | exact. de zéro | écart moyen pré-entraîné | écart moyen de zéro |
|---|---|---|---|---|---|
| discours | 101 | 44% | 40% | 0.62 | 0.77 |
| interjection | 65 | 72% | 52% | 0.28 | 0.48 |
| théâtre | 35 | 31% | 29% | 1.00 | 1.34 |
| poésie | 22 | 14% | 32% | 1.27 | 1.18 |
| question | 20 | 90% | 60% | 0.10 | 0.50 |
| réponse | 18 | 56% | 44% | 0.44 | 0.72 |
| roman | 11 | 27% | 64% | 0.91 | 0.36 |
| prose | 10 | 10% | 40% | 1.20 | 1.10 |
| texte officiel | 9 | 22% | 56% | 0.89 | 0.67 |
| procédure | 8 | 75% | 100% | 0.25 | 0.00 |
| conférence de presse | 7 | 43% | 57% | 0.71 | 0.86 |
| maxime | 6 | 17% | 17% | 0.83 | 1.33 |
| fable | 6 | 50% | 17% | 0.67 | 1.33 |
| tweet de marque | 5 | 60% | 60% | 0.40 | 0.40 |

Textes bien classés par le pré-entraîné seulement : 71 ; par le modèle de zéro seulement : 57.
