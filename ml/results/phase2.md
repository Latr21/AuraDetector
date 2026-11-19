## Phase 2 — évaluation finale unique sur le test réel (330 textes)

| Modèle | kappa val_domaine | Exactitude | ±1 | F1-macro | **Kappa test** | Rappel Anti | Rappel Corr | Rappel Forte | Rappel Divine |
|---|---|---|---|---|---|---|---|---|---|
| ensemble_combine | 0.949 | 59.4% | 91.8% | 0.45 | **0.389** | 51% | 77% | 32% | 21% |
| p2_cls_w3_ens3+seuils | 0.941 | 54.5% | 90.6% | 0.45 | **0.379** | 51% | 64% | 40% | 30% |
| p2_cls_w1_s42+seuils | 0.937 | 52.4% | 90.6% | 0.44 | **0.336** | 44% | 64% | 34% | 33% |
| p2_cls_w3_s43+seuils | 0.937 | 55.5% | 91.8% | 0.45 | **0.355** | 46% | 69% | 38% | 24% |
| p2_cls_w3_s42+seuils | 0.937 | 54.8% | 90.3% | 0.46 | **0.352** | 44% | 65% | 43% | 33% |
| p2_cls_w3_s42 | 0.933 | 54.5% | 90.3% | 0.45 | **0.352** | 46% | 65% | 40% | 30% |
| p2_reg_s43+seuils | 0.932 | 48.8% | 90.6% | 0.41 | **0.345** | 51% | 53% | 48% | 21% |
| p2_reg_s44+seuils | 0.931 | 59.1% | 91.2% | 0.47 | **0.366** | 49% | 76% | 28% | 36% |
| p2_cls_w2_s42+seuils | 0.931 | 51.5% | 88.8% | 0.43 | **0.357** | 41% | 61% | 35% | 39% |
| p2_cls_w1_s42 | 0.931 | 52.7% | 90.3% | 0.44 | **0.334** | 44% | 64% | 35% | 33% |
| p2_large_reg_s42+seuils | 0.930 | 56.4% | 92.1% | 0.46 | **0.386** | 44% | 67% | 49% | 24% |
| p2_cls_w3_s44+seuils | 0.930 | 50.3% | 90.6% | 0.38 | **0.313** | 54% | 61% | 35% | 12% |
| p2_cls_w3_s43 | 0.929 | 51.8% | 91.2% | 0.43 | **0.343** | 51% | 60% | 42% | 24% |
| p2_reg_s42+seuils | 0.929 | 57.0% | 92.1% | 0.48 | **0.387** | 51% | 65% | 51% | 27% |
| p2_reg_s42 | 0.927 | 57.0% | 91.8% | 0.46 | **0.368** | 51% | 69% | 43% | 24% |
| p2_reg_ens3+seuils | 0.925 | 51.5% | 91.5% | 0.44 | **0.356** | 49% | 59% | 45% | 27% |
| p2_cls_w2_s42 | 0.925 | 49.1% | 89.7% | 0.42 | **0.360** | 41% | 57% | 38% | 36% |
| p2_reg_s43 | 0.925 | 53.6% | 91.8% | 0.42 | **0.352** | 49% | 65% | 42% | 18% |
| p2_large_reg_s42 | 0.921 | 59.1% | 93.0% | 0.47 | **0.403** | 37% | 74% | 46% | 24% |
| p2_cls_w3_s44 | 0.919 | 49.1% | 89.7% | 0.41 | **0.327** | 54% | 53% | 48% | 21% |
| p2_reg_s44 | 0.910 | 55.2% | 91.2% | 0.44 | **0.349** | 51% | 67% | 42% | 18% |

Modèle retenu (meilleur kappa sur val_domaine, choisi AVANT de regarder le test) : **ensemble_combine**
composants : {'p2_large_reg_s42': 0.6000000000000001, 'p2_cls_w3_s42': 0.1333333333333333, 'p2_cls_w3_s43': 0.1333333333333333, 'p2_cls_w3_s44': 0.1333333333333333} ; seuils : (-12.0, 36.0, 69.0)

### Matrice de confusion (test réel)

| réf. \ prédit | Anti | Corr | Fort | Divi |
|---|---|---|---|---|
| **Anti** | 21 | 13 | 7 | 0 |
| **Corr** | 24 | 147 | 18 | 2 |
| **Fort** | 6 | 33 | 21 | 5 |
| **Divi** | 5 | 7 | 14 | 7 |

### 15 pires erreurs (test réel)

| id | type | texte | référence | prédiction (score) |
|---|---|---|---|---|
| T229 | discours | De l'audace, encore de l'audace, toujours de l'audace, et la France est sauvée ! | Aura Divine | Anti-Aura (-37) |
| T227 | prose | Parce que c'était lui, parce que c'était moi. | Aura Divine | Anti-Aura (-36) |
| T223 | théâtre | C'est un roc !… c'est un pic !… c'est un cap ! Que dis-je, c'est un cap ?… C'est une péninsule ! | Aura Divine | Anti-Aura (-27) |
| T284 | poésie | Nais, grandis, rêve, souffre, aime, vis, vieillis, tombe. | Aura Divine | Anti-Aura (-19) |
| T210 | poésie | Je suis belle, ô mortels ! comme un rêve de pierre, | Aura Divine | Anti-Aura (-17) |
| T238 | théâtre | Votre prudence est endormie, De traiter magnifiquement Et de loger superbement Votre plus cruelle ennemie. | Anti-Aura | Forte Aura (+66) |
| T240 | théâtre | L'espoir, il est vrai, nous soulage, Et nous berce un temps notre ennui ; | Anti-Aura | Forte Aura (+58) |
| T275 | roman | Car jamais je n’ai trouvé dans la société de personne un charme aussi complet. | Anti-Aura | Forte Aura (+57) |
| T239 | théâtre | Par ma foi ! il y a plus de quarante ans que je dis de la prose sans que j'en susse rien. | Anti-Aura | Forte Aura (+56) |
| T271 | roman | ce roi bien-aimé à qui aucune branche de la prospérité publique ou particulière n’est indifférente | Anti-Aura | Forte Aura (+51) |
| T234 | fable | Le Corbeau, honteux et confus, Jura, mais un peu tard, qu'on ne l'y prendrait plus. | Anti-Aura | Forte Aura (+48) |
| T257 | théâtre | Ah ?… Et moi, Cyrano-Savinien-Hercule De Bergerac. | Aura Divine | Aura Correcte (-11) |
| T279 | roman | Croyez-vous qu’il faille, pour être agronome, avoir soi-même labouré la terre ou engraissé des volailles ? | Anti-Aura | Forte Aura (+42) |
| T311 | débat | Moi, président de la République, je ferai en sorte que mon comportement soit en chaque instant exemplaire. | Forte Aura | Anti-Aura (-28) |
| T219 | poésie | Waterloo ! Waterloo ! Waterloo ! morne plaine ! | Forte Aura | Anti-Aura (-27) |

### Par type de texte : avant (CamemBERT régression, phase 1) / après (ensemble_combine)

| Type | n | exact. avant | exact. après | écart moyen avant | écart moyen après |
|---|---|---|---|---|---|
| discours | 101 | 44% | 58% | 0.62 | 0.49 |
| interjection | 65 | 72% | 86% | 0.28 | 0.14 |
| théâtre | 35 | 31% | 31% | 1.00 | 0.97 |
| poésie | 22 | 14% | 23% | 1.27 | 1.14 |
| question | 20 | 90% | 85% | 0.10 | 0.15 |
| réponse | 18 | 56% | 67% | 0.44 | 0.33 |
| roman | 11 | 27% | 36% | 0.91 | 0.91 |
| prose | 10 | 10% | 50% | 1.20 | 0.70 |
| texte officiel | 9 | 22% | 67% | 0.89 | 0.33 |
| procédure | 8 | 75% | 100% | 0.25 | 0.00 |
| conférence de presse | 7 | 43% | 71% | 0.71 | 0.29 |
| fable | 6 | 50% | 33% | 0.67 | 0.83 |
| maxime | 6 | 17% | 33% | 0.83 | 0.67 |
| tweet de marque | 5 | 60% | 60% | 0.40 | 0.40 |

Global : kappa 0.323 → 0.389 ; F1-macro 0.34 → 0.45

### Registre battle (val_domaine, 40 textes)

| réf. \ prédit | Anti | Corr | Fort | Divi |
|---|---|---|---|---|
| **Anti** | 10 | 0 | 0 | 0 |
| **Corr** | 0 | 10 | 0 | 0 |
| **Fort** | 0 | 0 | 9 | 1 |
| **Divi** | 0 | 0 | 1 | 9 |

Clashs spirituels (Forte/Divine) prédits Forte ou Divine : 100% (20/20) ; prédits Anti : 0. Anti prédits Anti : 10/10.
