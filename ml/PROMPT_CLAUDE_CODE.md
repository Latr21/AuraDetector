Tu reprends le projet "Aura Classifier" : un classifieur de textes français qui attribue un niveau d'"Aura" (charisme, statut, originalité, style, forme). Tout est dans ce dossier ; lis d'abord README.md.

CONTEXTE
- 4 classes, déduites d'un score de -100 à +100 :
  Anti-Aura (-100 à -11), Aura Correcte (-10 à +24), Forte Aura (+25 à +74), Aura Divine (+75 à +100).
- Score = 0,333·R + 0,222·S + 0,167·O + 0,167·B + 0,111·P (Rizz, Statut, Originalité, Beauté/style, Poésie/forme, chacune de -100 à +100).
- Règle centrale : on note l'aura de CELUI QUI ÉCRIT, pas le sujet. Une moquerie spirituelle d'un sujet gênant = Forte Aura ; l'autodérision drôle = Aura Correcte ; Anti-Aura = l'auteur lui-même est gênant (needy, try-hard, brainrot plaqué, langue de bois, insulte sèche). Un cliché n'est jamais Divine. On note la forme, jamais le camp politique ni l'opinion.
- data/train_synthetique.csv (6 991 textes générés) + data/grok_textes.csv (105 textes) = entraînement.
- data/test_reel.csv (330 vrais textes, annotés par une IA) = test. NE JAMAIS l'utiliser pour entraîner, choisir des hyperparamètres ou générer des données qui lui ressemblent.
- Référence actuelle (scripts/baseline.py, TF-IDF + régression logistique) : kappa quadratique 0,05 (classification) et 0,15 (régression) sur le test réel. Toujours répondre "Aura Correcte" donne 58 % d'exactitude : l'indicateur principal est le KAPPA QUADRATIQUE, puis le F1-macro et la matrice de confusion.

TÂCHES, dans l'ordre (crée une liste de tâches et coche au fur et à mesure)

1. Environnement
   - Crée un venv, installe requirements.txt. Vérifie si un GPU (CUDA ou Apple MPS) est disponible et dis-le-moi.
   - Lance `python scripts/baseline.py` et confirme que tu retrouves à peu près les chiffres de référence.

2. Paires contrastées (le modèle actuel associe le THÈME à la classe au lieu de la FORME)
   - Écris 400 paires dans data/paires_contrastees.csv (colonnes : texte,classe,score,style,origine,paire_id ; origine = "paires_contrastees").
   - Dans chaque paire, les deux textes partagent le même sujet et une bonne partie du vocabulaire, mais ont une aura opposée ou très différente. Exemples de couples : brainrot plaqué ("dab dab, six-seven") vs anecdote brainrot drôle et bien amenée ; phrase politique plate avec "leader/président" vs réplique politique qui fait mouche ; proverbe usé vs maxime inventée avec jeu de mots ; insulte sèche vs pique ironique ; drague lourde vs drague drôle et assurée ; info neutre vs même info racontée avec style.
   - Répartis sur les 4 classes (au moins 150 textes par classe au total), varie les registres (SMS, bio, tweet, discours, prose, brainrot), les longueurs et les styles politiques (tous bords, sans nommer de personnes réelles, aucun contenu haineux).
   - Interdit : recopier ou paraphraser de près un texte de data/test_reel.csv. Vérifie-le automatiquement (aucune séquence de 6 mots commune avec le test, aucun texte court identique) et retire les fautifs.
   - Relance baseline.py en ajoutant ce fichier à l'entraînement et compare les kappas.

3. CamemBERT
   - scripts/train_camembert.py n'a jamais été exécuté (écrit sans accès à PyTorch) : lance-le, corrige les bugs éventuels sans changer la logique (le test réel reste hors entraînement ; la validation est tirée du train).
   - Entraînement : --train data/train_synthetique.csv data/grok_textes.csv data/paires_contrastees.csv
   - Fais tourner les deux modes : classification puis --mode regression. Sans GPU, commence par --epochs 1 sur un sous-échantillon pour vérifier que tout marche, puis préviens-moi du temps estimé avant un entraînement complet.
   - Si la classe Aura Divine est mal reconnue (elle a moins d'exemples), ajoute une pondération des classes dans la loss et compare.

4. Deuxième IA : réseau de neurones entraîné de zéro (sans aucun pré-entraînement)
   Objectif : comparer CamemBERT (pré-entraîné) à des réseaux qui n'apprennent QUE sur nos données, construits avec les briques vues en cours (neurone, activations, couches denses, softmax, entropie croisée, rétropropagation, mini-batches, Adam, early stopping, embeddings, LSTM).
   - Interdit : poids pré-entraînés, embeddings pré-entraînés (word2vec, fastText, GloVe…), tokenizer pré-entraîné de Hugging Face. Tout est initialisé au hasard (graine fixée) et appris sur train_synthetique + grok_textes + paires_contrastees.
   - 4a. scripts/mlp_numpy.py : perceptron multicouche écrit à la main en NumPy, comme le labo du cours.
     · Entrée : TF-IDF (TfidfVectorizer ajusté sur le train uniquement, mots + n-grammes de caractères 2–5, max ~20 000 features).
     · Architecture : entrée → couche cachée (128, tanh ou ReLU) → couche cachée (64) → sortie 4 neurones + softmax.
     · Propagation avant et rétropropagation codées à la main (règle de la chaîne), initialisation Xavier/He, perte entropie croisée pondérée par classe, mini-batches de 64, optimiseur Adam codé à la main (m, v, correction de biais), dropout simple.
     · Vérifie le gradient sur un petit lot par différences finies (gradient check) avant d'entraîner.
   - 4b. scripts/train_from_scratch.py : réseau PyTorch sans pré-entraînement.
     · Tokenisation maison (minuscules, regex mots + ponctuation + emojis), vocabulaire construit sur le train uniquement (fréquence ≥ 2, token <UNK>, <PAD>).
     · Architecture : Embedding (dim 128, initialisé au hasard) → BiLSTM (1 ou 2 couches, 128 unités) → pooling (max + moyenne, ou attention additive simple) → Dense + dropout → sortie.
     · Deux modes comme CamemBERT : classification (4 neurones + softmax, entropie croisée avec poids de classes) et --mode regression (1 neurone linéaire sur le score, MSE, puis conversion en classe avec les seuils officiels).
     · Adam, gradient clipping, early stopping sur la validation (tirée du train, stratifiée), sauvegarde du meilleur modèle.
   - Pour les deux : validation tirée du train uniquement ; même graine ; enregistre les courbes de loss train/validation (PNG) dans results/ et commente-les (sous-apprentissage, surapprentissage, moment de l'early stopping).
   - Petite recherche d'hyperparamètres SUR LA VALIDATION seulement (learning rate, taille cachée, dropout), 6 à 10 essais maximum, résumés dans un tableau.
   - Ces modèles tournent sur CPU : donne le temps d'entraînement de chacun.
   - Ajoute à scripts/predire.py une option --modele {camembert,mlp_numpy,bilstm} pour pouvoir les tester comme CamemBERT.

5. Évaluation et analyse
   - Tableau comparatif sur le test réel : baseline / baseline + paires / CamemBERT classif / CamemBERT régression / MLP NumPy / BiLSTM classif / BiLSTM régression, avec exactitude, à ±1 classe, F1-macro, kappa quadratique, temps d'entraînement et nombre de paramètres.
   - Matrice de confusion du meilleur modèle, et les 15 pires erreurs (texte, référence, prédiction) avec une hypothèse courte pour chacune.
   - Compare explicitement le meilleur modèle pré-entraîné et le meilleur modèle entraîné de zéro : sur quelles classes et quels types de textes le pré-entraînement aide-t-il ?
   - Teste le meilleur modèle ET le meilleur modèle entraîné de zéro avec scripts/predire.py sur ces phrases : "Je me suis chié dessus" ; "La bière c'est comme ma femme, brune et amer" ; "fort en chocolat" ; "dab dab, six-seven" ; "un accident de train a eu lieu en espagne ce samedi," ; "En imposer pour ne pas avoir à imposer, voilà en quoi consiste le charisme." ; "Loin des yeux, loin du cœur". Mes classes attendues : Anti, Anti, Correcte, Anti, Correcte, Forte, Correcte.

6. Rapport
   - Écris RESULTATS.md : ce qui a été fait, le tableau, ce qui a marché ou non, une section « pré-entraîné vs entraîné de zéro » avec les courbes de loss, et les 3 prochaines actions les plus utiles.

RÈGLES
- Ne modifie jamais data/test_reel.csv ni data/test_annotateur_vierge.csv.
- Ne collecte aucun texte de personnes privées (Reddit, Instagram, messages…) : vie privée.
- Ne commite rien, ne pousse rien en ligne.
- Si une étape bloque (pas de GPU, téléchargement du modèle impossible…), explique-le et propose une alternative au lieu de contourner en silence.
