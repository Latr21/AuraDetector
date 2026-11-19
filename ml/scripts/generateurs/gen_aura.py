import random, csv
from itertools import combinations

R = random.Random(2026)
p = R.choice

def typo(t, prob=0.6):
    subs = [("c'est", "cé"), ("je suis", "jsuis"), ("pourquoi", "pk"), ("beaucoup", "bcp"),
            ("vraiment", "vrmt"), ("aujourd'hui", "ajd"), ("quoi", "koi"), ("tu es", "t'es"),
            ("je sais pas", "jsp"), ("s'il te plaît", "stp"), ("tout le monde", "tlm"),
            ("quand même", "qd mm"), ("rien", "r1"), ("toujours", "tjr"), ("bien", "b1")]
    for a, b in subs:
        if a in t and R.random() < prob:
            t = t.replace(a, b)
    return t

# ---------------------------------------------------------------- ANTI-AURA
def a_relance():
    g = p(["slt", "coucou", "wesh", "hey", "bjr", "re", "allo ?", "yo", "cc"])
    q = p(["tu dors ?", "t'as vu mon msg ?", "pourquoi tu réponds pas", "tu m'en veux ?", "t'es là ?",
           "tu m'as bloqué ou quoi", "t'as perdu ton tel ?", "je te dérange ?"])
    m = p(["ça fait 3 jours que j'attends", "j'ai vu que t'étais en ligne y'a 2 min",
           "t'as mis une story mais tu réponds pas à moi", "je sais que t'as lu, y'a les deux traits bleus",
           "j'ai demandé à ta pote, elle dit que t'es occupée", "je suis pas jaloux hein je demande juste",
           "j'ai écrit ton prénom sur ma main au stylo", "ma mère demande de tes nouvelles aussi",
           "j'ai rechargé la conv 40 fois"])
    e = p(["bon ok", "😢😢😢", "...", "je te laisse tranquille (pas vraiment)", "réponds stp 🥺",
           "c'est pas grave j'ai l'habitude", "bref bonne nuit quand même ❤️❤️❤️", "je vais attendre ici",
           "je compte jusqu'à 100 et je renvoie"])
    t = p(["\n", " ", " / "]).join([f"{g} {q}", m, e])
    return typo(t), p(["Relance désespérée qui pulvérise tout charisme.",
                       "Insistance needy et anxieuse, aura en chute libre.",
                       "Le triple texto non répondu : signature de la défaite."]), (0.0, 0.55)

def a_bio():
    intro = p(["Pas là pour les prises de tête.", "Je cherche ma reine 👑", "Entrepreneur dans l'âme 💸",
               "Mec simple, j'aime la vie.", "Ici pour trouver la mère de mes futurs enfants.",
               "Alpha mais avec un grand coeur 🐺❤️"])
    d = R.sample(["1m78 (oui ça compte)", "j'aime pas les filles compliquées", "si t'as un Snap vide passe ton chemin",
                  "je suis un gentleman pas comme les autres", "Sigma mindset", "je réponds pas aux 'salut'",
                  "j'ai une voiture", "pas de daronne relou svp", "je suis sapiosexuel (j'ai lu un livre)"], 2)
    end = p(["Swipe à droite si t'es pas superficielle.", "Bonus si tu cuisines 😏", "Snap : kevdu93_officiel",
             "DM si t'es prête à être aimée.", "Mon ex dit que je suis toxique mais elle ment.",
             "Les filles à frange s'abstenir."])
    t = f"{intro} {d[0].capitalize()}, {d[1]}. {end}"
    return t, p(["Bio qui empile les red flags et une posture alpha ratée.",
                 "Exigences agressives et ego fragile : repoussoir absolu.",
                 "Cringe de profil Tinder niveau musée."]), (0.1, 0.7)

def a_grind():
    x = p(["dormez", "scrollez TikTok", "allez en soirée", "regardez Netflix", "pleurez pour votre ex", "mangez des chips"])
    y = p(["build mon empire", "me lève à 4h47", "bois mon eau citronnée en visualisant mes millions",
           "lis 3 pages de Père Riche Père Pauvre", "fais du dropshipping de coques de téléphone",
           "regarde des vidéos sur la discipline", "écris mes objectifs sur un post-it"])
    z = p(["Les loups ne demandent pas la permission.", "Le succès c'est un état d'esprit 🧠.",
           "Personne croyait en moi, à part ma grand-mère.", "Bientôt la Lambo, patience.",
           "Vous allez regretter de m'avoir sous-estimé.", "J'ai 19 ans et je suis déjà fatigué de votre médiocrité."])
    tag = p(["🦁🔥 #grindset", "🐺💯 #sigma", "💸💸 #mindset #motivation", "#entrepreneur #nopainnogain", "👑👑"])
    t = f"Pendant que vous {x}, moi je {y}. {z} {tag}"
    return t, p(["Dominance autoproclamée et creuse, cringe motivationnel pur.",
                 "Le statut revendiqué tue le statut réel.",
                 "Grindset de façade : aucune substance, que du bruit."]), (0.2, 0.9)

def a_jalousie():
    x = p(["au ciné", "à la salle", "manger un kebab", "au bowling", "à l'anniv de Léa", "faire les courses", "au Ikea"])
    y = p(["Kevin", "ton cousin", "tes potes", "Jordan", "ton coloc", "ce mec de ta classe", "Mathéo"])
    z = p(["😤", "bonne soirée hein", "de toute façon j'avais prévu un truc", "t'inquiète je vais jouer à Fortnite seul",
           "je vais le dire à ta mère", "j'ai même pas faim de toute façon"])
    t = f"ok donc tu préfères aller {x} avec {y} plutôt qu'avec moi ? super. vraiment super. non mais vas-y amuse-toi. je suis pas fâché. JE SUIS PAS FÂCHÉ. {z}"
    return typo(t, 0.4), p(["Passif-agressif puéril, zéro maîtrise de soi.",
                            "Crise de jalousie en majuscules : aura vaporisée.",
                            "Fragilité émotionnelle exposée sans le moindre style."]), (0.1, 0.6)

def a_poeme():
    x = p(["une pizza 4 fromages", "ma Clio 2 après le lavage", "un frigo plein", "le Wi-Fi qui capte bien",
           "un samedi sans réveil", "une remise de 20%", "un kebab sauce blanche"])
    y = p(["Mon coeur il fait boum boum", "Quand je te vois je deviens tout rouge", "Tes yeux sont des yeux",
           "Je pense à toi même aux toilettes", "Tu es mon soleil, mon parasol aussi"])
    z = p(["Je t'aime plus que la PS5", "Je t'aime plus que le PSG (presque)", "Tu es la plus mieux du monde",
           "Je sais pas ce qui rime avec toi", "Tes cheveux sentent le shampoing"])
    w = p(["Réponds stp", "Signé : ton admirateur secret (c'est Romain)", "Fin du poème", "❤️❤️❤️❤️",
           "Voilà c'est tout ce que j'ai"])
    t = f"Tu es belle comme {x}\n{y}\n{z}\n{w}"
    return t, p(["Comparaisons absurdes, aucune rime, aucune élégance.",
                 "Tentative poétique qui insulte la poésie et la destinataire.",
                 "Rythme inexistant et images de supermarché."]), (0.15, 0.75)

def a_approche():
    x = p(["Salut", "Bonsoir", "Hey", "Cc", "Wesh"])
    y = p(["t'es trop charmante j'ai pas pu m'empêcher", "je t'ai vue passer et j'ai dit c'est elle",
           "t'as un sourire qui m'a mis KO", "t'as l'air d'une fille bien pas comme les autres"])
    z = p(["T'as un 06 ?", "On se capte quand ?", "Tu me donnes ton Snap ?", "Je t'offre un Oasis ?"])
    w = p(["Pourquoi tu réponds pas ? Tu fais ta difficile ?", "Allez sois pas timide 😏",
           "T'es moins jolie quand tu ignores les gens en vrai.", "Bon t'es moche de toute façon.",
           "Ok bah t'es une hautaine."])
    t = f"{x} ma belle, {y}. {z}\n{w}"
    return typo(t, 0.3), p(["Drague lourde qui vire à l'aigreur, anti-charisme total.",
                            "Le revirement vexé après le refus : aura négative certifiée.",
                            "Insistance et insulte finale, rien à sauver."]), (0.0, 0.45)

def a_spam():
    a = p(["first 🥇🥇", "qui regarde en 2026 ?? 👇👇", "mdr j'ai pas compris mais like", "TROP BIEN",
           "pov : toi qui lis ce commentaire", "abonnez vous a moi svp", "1 like = 1 prière"])
    b = p(["je suis à 12 abonnés aidez moi 😭", "allez on fait monter ce com", "jsuis le seul a pas avoir ri ?",
           "check ma chaîne j'ai fait un remix", "flemme d'écrire un vrai com", "dédicace à mon frère Yanis"])
    return typo(f"{a} {b}", 0.5), p(["Mendicité numérique en commentaire, présence nulle.",
                                     "Bruit de fond d'internet, aucune personnalité.",
                                     "Commentaire réflexe et quémandeur."]), (0.35, 1.0)

A_FIXED = [
    ("jsuis pas comme les autres mecs moi jsuis un mec bien. jtai tenu la porte au McDo tu t'en souviens ? bah voila. maintenant tu me dois un rdv", "Galanterie transactionnelle qui réclame un dû."),
    ("Bonjour à tous, je me présente : Gérald, 34 ans, chef de rayon. Ma passion c'est d'expliquer aux gens pourquoi ils ont tort.", "Présentation suffisante et insupportable."),
    ("mdrrr jsuis tombé dans les escaliers devant toute la classe et après jai dit que c'était fait exprès pour le tiktok", "Humiliation aggravée par un mensonge minable."),
    ("Mon horoscope dit que je vais rencontrer l'amour cette semaine donc si t'es une fille et que tu lis ça c'est peut-être toi 👀👀", "Drague générique et pathétique au hasard."),
    ("Je t'ai offert un kebab, une rose de chez Total et un porte-clés Tour Eiffel. Et tu me friendzone ??", "Comptabilité amoureuse et rancune mesquine."),
    ("PERSONNE ME RESPECTE DANS CETTE FAMILLE même le chien il m'écoute pas", "Plainte criarde qui admet zéro statut."),
    ("bonjour madame la boulangère vous êtes très belle aujourd'hui est-ce que je peux avoir une baguette et votre numéro", "Drague déplacée et maladroite dans la file d'attente."),
    ("Je suis un génie incompris, j'ai inventé le concept de mettre du ketchup sur les céréales.", "Génie autoproclamé et idée répugnante."),
    ("hé t'as vu jai 3 fois plus de followers que toi sur insta 🤣 (jen ai acheté mais chut)", "Vantardise frauduleuse avouée."),
    ("Je ne pleure pas, ce sont mes yeux qui transpirent ma tristesse de mâle sigma incompris 😔🐺", "Mélodrame alpha totalement grotesque."),
    ("Salut c'est encore moi, le gars du 4ème, j'ai trouvé ta culotte dans la machine commune je te la garde ? 😏", "Malaise absolu et clin d'œil inquiétant."),
    ("jai rompu avec elle par message vocal de 14 minutes en pleurant mais c'était MOI qui partais attention", "Rupture pathétique racontée avec fierté."),
    ("Nan mais moi j'ai jamais tort. Une fois j'ai cru que j'avais tort mais en fait je m'étais trompé.", "Ego démesuré et logique en court-circuit."),
    ("J'ai mis 3h à écrire ce message pour te dire que je t'aime pas du tout et que je pense pas à toi.", "Déni qui hurle l'obsession."),
    ("Mes amis disent que je suis lourd mais en vrai c'est eux qui sont trop légers lol", "Retournement d'argument navrant."),
    ("je repost des citations de Lao Tseu en story mais jai jamais lu un livre de ma vie 🙏✨", "Sagesse d'emprunt et vacuité assumée."),
    ("Bonjour, j'ai été licencié mais je considère que c'est eux qui m'ont perdu. Je cherche un poste de CEO.", "Déni grandiose et ambition délirante."),
    ("t'es pas d'accord ? ok bah bloque moi. non pas toi, toi tu restes. bon si en fait bloque moi. JE PLAISANTE", "Instabilité totale en quatre phrases."),
    ("Mon type de femme : belle, intelligente, drôle, riche, qui ne parle pas trop. Moi : là.", "Exigences démesurées pour zéro contrepartie."),
    ("cc la miss tu veux voir ma collection de casquettes ? jen ai 47 dont 3 dédicacées par des youtubeurs", "Proposition ridicule et vantardise de niche."),
]
def a_fixed():
    t, j = p(A_FIXED); return t, j, (0.0, 1.0)

# ---------------------------------------------------------------- AURA FAIBLE
def f_hesitant():
    x = p(["je sais pas si tu te souviens de moi, on était en TD de stats ensemble", "c'est Thomas, le pote de Julien",
           "on s'est croisés à la soirée de samedi, j'étais celui qui a renversé le punch",
           "je t'écris parce que t'as liké ma photo y'a 2 ans", "on était au même arrêt de bus ce matin",
           "c'est moi qui t'ai demandé un stylo en amphi"])
    y = p(["enfin bref je voulais savoir si t'avais les notes de mardi ?",
           "bref je me demandais si tu voulais peut-être, enfin si t'as le temps, boire un café ?",
           "bon c'est pas important en fait", "du coup voilà, je dis bonjour",
           "enfin je sais pas trop pourquoi j'écris en fait"])
    z = p(["pas grave sinon hein", "dsl encore", "oublie si c'est bizarre 😅", "bonne journée !! (ou soirée)", ""])
    t = f"euh salut, désolé de te déranger, {x}… {y} {z}".strip()
    return t, p(["Gentil mais noyé sous les excuses et l'hésitation.",
                 "Message timide qui s'auto-sabote avant la fin.",
                 "Intention correcte, exécution qui transpire le malaise."]), (0.0, 0.7)

def f_bio():
    a = p(["Je sais jamais quoi mettre dans les bios lol.", "Nouveau sur l'appli, c'est mon pote qui m'a inscrit.",
           "Bon bah voilà ma bio.", "Pas doué pour me décrire.", "Bio en cours de rédaction depuis 2023."])
    b = p(["J'aime bien manger et dormir.", "Fan de Marvel et de pâtes au beurre.", "Je regarde beaucoup de séries.",
           "J'ai un chat qui s'appelle Chat.", "Je fais du sport (parfois) (rarement).", "J'aime les voyages, comme tout le monde."])
    c = p(["Voilà.", "Écris-moi si tu veux, ou pas.", "On verra bien 🤷", "Je réponds lentement désolé.", "Bref."])
    return f"{a} {b} {c}", p(["Bio sans effort ni relief, attractivité en berne.",
                              "Autodérision molle qui ne donne envie de rien.",
                              "Aucune singularité, aucune promesse."]), (0.2, 1.0)

def f_excuse():
    x = p(["j'ai raté le bus", "mon réveil a pas sonné", "j'ai oublié mes clés", "je me suis trompé de ligne"])
    y = p(["le deuxième bus était plein", "j'ai dû retourner chez moi", "j'ai renversé mon café sur mon pantalon",
           "Google Maps m'a envoyé dans un champ"])
    z = p(["je me suis trompé de sortie", "j'ai croisé ma tante", "mon téléphone s'est éteint", "il pleuvait"])
    w = p(["Je suis vraiment nul, pardon.", "Je comprendrais si vous commencez sans moi.", "Encore désolé, vraiment.",
           "J'arrive dans 25 min (ou 40)."])
    return f"Désolé désolé désolé pour le retard, {x}, puis {y}, puis {z}. {w}", p(
        ["Avalanche d'excuses qui projette une image brouillonne.",
         "Auto-flagellation en série, statut au ras du sol.",
         "Chaos logistique raconté sans panache."]), (0.1, 0.8)

def f_linkedin():
    a = p(["Aujourd'hui, mon fils de 4 ans a refusé de ranger ses jouets.", "Ce matin, un inconnu m'a demandé l'heure.",
           "Hier, j'ai raté mon train.", "Mon chat a renversé mon café sur mon clavier.", "J'ai fait un footing de 2 km."])
    b = p(["Et c'est là que j'ai compris le vrai sens du leadership.", "Ça m'a appris plus que 10 ans de MBA.",
           "J'ai réalisé que l'échec est une opportunité.", "Et j'ai pensé à la résilience de nos équipes."])
    c = p(["Le client, c'est comme un enfant : il faut l'écouter.", "La vie est un KPI qu'on ne mesure pas.",
           "Soyez le café qui se renverse dans la vie des autres.", "Agilité. Humilité. Synergie."])
    d = p(["Qu'en pensez-vous ? 👇", "Likez si vous êtes d'accord 🙏", "Je suis humble d'avoir compris ça.", "Agree ?"])
    tag = p(["#leadership #résilience", "#management #inspiration", "#growth #mindset", "#humilité #team"])
    return f"{a}\n\n{b}\n\n{c}\n\n{d} {tag}", p(["Humble-brag LinkedIn qui se veut profond et sonne creux.",
                                                  "Parabole managériale forcée, gêne palpable.",
                                                  "Fausse sagesse corporate, originalité négative."]), (0.0, 0.6)

def f_poeme_plat():
    L = ["La pluie tombe sur la ville", "Je suis triste", "Les gens marchent", "La vie continue", "Le ciel est gris",
         "J'ai mangé une pomme", "Mon cœur est un peu cassé", "Le bus est en retard", "Il fait froid dehors",
         "Je pense à des choses", "Les arbres sont des arbres", "Demain sera un autre jour"]
    lines = R.sample(L, R.choice([3, 4, 5])) + [p(["Voilà", "Fin", "Bref", "(poème écrit en cours de SVT)"])]
    return "\n".join(lines), p(["Poème scolaire sans rythme ni image marquante.",
                                "Vers plats qui constatent au lieu d'évoquer.",
                                "Mélancolie de surface, forme absente."]), (0.3, 1.0)

def f_mystere():
    x = p(["très mystérieux", "très complexe", "difficile à cerner", "assez sombre au fond", "une énigme"])
    y = p(["Peu de gens me comprennent vraiment.", "Mon âme est vieille.", "Je vis la nuit (et aussi un peu le jour).",
           "Mes potes disent que je suis un loup solitaire.", "J'ai beaucoup souffert (au collège)."])
    z = p(["🌙 Mais j'aime aussi les crêpes.", "🖤 Sinon je bosse chez Décathlon.", "(je suis Capricorne)", "Bref.",
           "🐺✨", "Like si toi aussi."])
    return f"Je suis quelqu'un de {x}. {y} {z}", p(["Mystère autoproclamé, donc évaporé instantanément.",
                                                    "Profondeur revendiquée puis sabotée par la chute.",
                                                    "Pose ténébreuse en carton."]), (0.2, 1.0)

def f_vocal():
    x = p(["euh je t'appelle pour", "ouais donc en fait je voulais te dire", "attends je suis dans le métro, euh",
           "allô ? ah c'est la messagerie, euh"])
    y = p(["ouais non c'est bon j'ai retrouvé mes clés en fait", "je sais plus ce que je voulais dire",
           "rappelle-moi, enfin si tu veux", "c'était pour le truc, tu sais, le truc"])
    return f"[vocal] ouais allô c'est moi, {x}… attends… {y}, bon ben salut, bisous, enfin salut", p(
        ["Message confus et inutile, présence quasi nulle.",
         "Hésitations en cascade, aucune intention claire.",
         "Vocal-labyrinthe qui épuise l'auditeur."]), (0.3, 1.0)

F_FIXED = [
    ("T'es pas si moche que ce que je pensais en vrai 😅", "Compliment empoisonné qui se croit sympa."),
    ("Je vais me mettre au sport lundi. Ça fait 4 lundis que je dis ça mais là c'est le bon.", "Résolution molle et auto-sabotée."),
    ("Ma passion ? Euh… les gens ? Et le fromage. Surtout le fromage.", "Réponse improvisée sans conviction."),
    ("Coucou ! Petit rappel : il reste des parts de gâteau en salle de pause 🎂 Elles sont un peu sèches mais bon.", "Message gentil mais qui se dévalorise lui-même."),
    ("J'ai essayé d'être drôle à la réunion. Personne a ri. J'ai fait semblant de tousser.", "Anecdote de gêne sans rebond."),
    ("Bonjour, je voudrais savoir si c'est normal que mon gâteau ressemble à une omelette ?", "Question touchante mais cocasse et maladroite."),
    ("Mdr je sais pas danser mais je danse quand même, faut bien vivre 🤪", "Bonne énergie mais aucune maîtrise."),
    ("Je t'ai acheté un cadeau mais je l'ai oublié dans le train. C'est l'intention qui compte non ?", "Gentillesse plombée par la maladresse."),
    ("Mon rêve c'est d'ouvrir un food truck de soupes. Même l'été. Surtout l'été.", "Ambition attachante mais peu crédible."),
    ("Je voulais faire une déclaration mais j'ai paniqué et j'ai dit 'bon appétit' à 16h.", "Panique sociale racontée sans panache."),
    ("Ok je l'avoue : je parle à mes plantes et elles meurent quand même.", "Autodérision sympathique mais faible."),
    ("Salut la team ! Qui est chaud pour un afterwork ? Personne ? Ok je vais me coucher.", "Proposition abandonnée avant même la réponse."),
    ("Je me suis coupé les cheveux moi-même pendant le confinement. Je les recoupe depuis pour réparer.", "Récit maladroit, image peu flatteuse."),
    ("J'ai mis une chemise pour le rdv. Elle est trop grande. C'est celle de mon père.", "Détail touchant qui affaiblit la présence."),
    ("Moi aussi j'ai un côté rebelle : une fois j'ai pas rembobiné une cassette.", "Rébellion inoffensive, humour un peu daté."),
]
def f_fixed():
    t, j = p(F_FIXED); return t, j, (0.0, 1.0)

# ---------------------------------------------------------------- AURA NEUTRE
def n_logistique():
    a = p(["Salut à tous,", "Bonjour,", "Hello l'équipe,", "Coucou,"])
    b = p(["la réunion de lundi", "le point d'équipe de jeudi", "l'entraînement de mercredi", "le cours de demain", "le dîner de samedi"])
    c = p(["est décalé à 14h", "est avancé à 9h30", "est annulé", "aura lieu en salle B", "se fera en visio"])
    d = p(["Pensez à ramener vos ordinateurs.", "Merci de confirmer votre présence.", "Le lien sera envoyé par mail.",
           "Rien d'autre à signaler.", "Bonne journée."])
    return f"{a} {b} {c}. {d}", p(["Message logistique purement informatif.", "Information claire, aucune personnalité.",
                                  "Communication fonctionnelle et neutre."]), (0.0, 1.0)

def n_courses():
    items = R.sample(["du lait", "des œufs", "du PQ", "du pain", "des pâtes", "du café", "de la lessive", "des tomates", "du beurre"], 3)
    end = p(["Tu passes au Carrefour ?", "Je m'en occupe demain sinon.", "Merci !", "Ou on commande.", "Dis-moi."])
    return f"Faut racheter {items[0]}, {items[1]} et {items[2]}. {end}", p(
        ["Liste de courses banale, aura plate.", "Échange domestique sans relief.", "Pur utilitaire du quotidien."]), (0.1, 0.9)

def n_transport():
    a = p(["Le train de 18h12", "Le RER B", "Le bus 38", "Mon vol", "Le TER pour Nantes", "Le tram"])
    b = p(["a 10 minutes de retard", "est supprimé", "part de la voie 7", "est à l'heure", "est dévié à cause des travaux"])
    c = p(["J'arrive vers 19h.", "Je te tiens au courant.", "Commencez sans moi.", "", "Rien de grave."])
    return f"{a} {b}. {c}".strip(), p(["Information de transport, aucune charge émotionnelle.",
                                      "Constat factuel neutre.", "Message pratique sans style."]), (0.0, 1.0)

def n_bio():
    a = p(["Prof de maths à Lyon.", "Infirmière.", "Développeur web.", "Étudiant en droit.", "Comptable.", "Kiné à Rennes."])
    b = p(["Course à pied le dimanche.", "J'aime le cinéma et la randonnée.", "Lecture, cuisine, voyages.",
           "Un peu de guitare.", "Je joue au badminton."])
    c = p(["Café noir.", "Plutôt du matin.", "Recherche quelque chose de sérieux.", "", "Chat ou chien, je m'adapte."])
    return f"{a} {b} {c}".strip(), p(["Bio descriptive et correcte, sans saveur particulière.",
                                     "Informations neutres, ni charme ni malaise.",
                                     "Profil standard, sans relief."]), (0.2, 1.0)

def n_avis():
    a = p(["Livraison rapide, produit conforme.", "Bon rapport qualité-prix.", "Correct pour le prix.",
           "Le service était lent mais aimable.", "Chambre propre, petit-déjeuner moyen."])
    b = p(["Rien à redire.", "Je recommande.", "Sans plus.", "Je reviendrai peut-être.", "Emballage un peu abîmé."])
    return f"{a} {b} {p(['4/5', '3/5', '3,5/5', '★★★☆☆', '★★★★☆'])}", p(
        ["Avis client fonctionnel et neutre.", "Évaluation factuelle sans émotion.", "Retour standard, aucune voix propre."]), (0.0, 1.0)

def n_meteo():
    a = p(["Il va pleuvoir demain apparemment", "Ils annoncent du vent cet après-midi", "Il fait 12 degrés ce matin",
           "Grand soleil prévu ce week-end", "Risque d'orage ce soir"])
    b = p(["prends un parapluie", "couvre-toi", "on mange dehors si ça tient", "à voir", "on verra"])
    return f"{a}, {b}.", p(["Small talk météo, aura parfaitement neutre.", "Échange pratique sans enjeu.",
                           "Banalité du quotidien."]), (0.1, 1.0)

def n_mail():
    a = p(["Bonjour,", "Bonjour Madame,", "Bonjour Monsieur Martin,", "Bonjour à tous,"])
    b = p(["veuillez trouver ci-joint le document demandé.", "je reviens vers vous concernant votre demande.",
           "je vous confirme la réception de votre dossier.", "je serai absent du 12 au 16."])
    c = p(["Je reste à votre disposition.", "N'hésitez pas si besoin.", "Bonne réception.", ""])
    d = p(["Cordialement,", "Bien à vous,", "Bonne journée,"])
    e = p(["Claire Dubois", "J. Martin", "Service client", "Sophie"])
    return f"{a} {b} {c} {d} {e}".replace("  ", " "), p(["Mail administratif standard.", "Formule de politesse neutre, zéro aura.",
                                                         "Correspondance professionnelle impersonnelle."]), (0.1, 1.0)

N_FIXED = [
    ("Je suis rentré. Bonne nuit.", "Message minimal et neutre."),
    ("Tu peux sortir le linge de la machine ?", "Demande domestique sans enjeu."),
    ("On commande des pizzas ou on cuisine ?", "Question banale du quotidien."),
    ("La photocopieuse du 2ème est encore en panne.", "Constat de bureau sans relief."),
    ("Ok ça marche, à demain.", "Validation simple, ni positive ni négative."),
    ("J'ai fini le livre. Pas mal, la fin est un peu longue.", "Avis tiède et sans style."),
    ("Rendez-vous chez le dentiste mardi à 10h.", "Rappel purement factuel."),
    ("Le magasin ferme à 19h le samedi.", "Information pratique neutre."),
    ("Je regarde le match ce soir, tu viens ?", "Invitation banale sans charge."),
    ("Mon téléphone est à 3%, je te rappelle plus tard.", "Logistique pure."),
    ("Il reste du gratin dans le frigo si tu veux.", "Info domestique neutre."),
    ("La réunion a duré deux heures. On a parlé du budget.", "Compte rendu plat."),
    ("Je prends le métro, j'arrive dans 20 minutes.", "Message pratique sans relief."),
    ("Bon anniversaire ! Passe une bonne journée.", "Vœu standard, poli mais générique."),
    ("J'ai changé de forfait, c'est moins cher.", "Information anodine."),
    ("C'est quoi le code du portail déjà ?", "Question pratique neutre."),
]
def n_fixed():
    t, j = p(N_FIXED); return t, j, (0.0, 1.0)

# ---------------------------------------------------------------- AURA CORRECTE
def c_humour():
    a = p(["Je passe te prendre à 20h.", "Je ramène le dessert.", "Je suis en bas.", "J'ai réservé pour 21h.", "J'apporte le vin."])
    b = p(["Si t'es pas prête, je mange tes chips en t'attendant, c'est la règle.",
           "Si c'est raté, on dira que c'est de l'art contemporain.",
           "Je klaxonne pas, je suis un gentleman, mais je fixe ta fenêtre très fort.",
           "En cas de retard, je commande pour toi et j'assume mes choix.",
           "Si tu juges ma playlist, tu rentres à pied."])
    return f"{a} {b}", p(["Humour léger et assuré, charisme sympathique.", "Petite taquinerie bien dosée.",
                          "Message vivant avec une pointe d'esprit."]), (0.2, 1.0)

def c_bio():
    a = p(["Ingénieure le jour, pâtissière ratée la nuit.", "Prof de français qui corrige aussi les menus de restaurant.",
           "Architecte qui dessine surtout des plans sur la comète.", "Infirmier, cuisinier du dimanche, champion de Mario Kart.",
           "Libraire, donc je juge les livres par leur couverture."])
    b = p(["Je cherche quelqu'un qui goûtera mes échecs avec le sourire 🍰", "Bonus si tu connais un bon spot de ramen.",
           "Viens avec une recommandation de livre, repars avec une meilleure.", "Je perds au Uno avec beaucoup de dignité.",
           "Plutôt balade que boîte de nuit."])
    return f"{a} {b}", p(["Bio drôle et personnelle, attractive sans forcer.", "Autodérision maîtrisée et charmante.",
                          "Personnalité visible en deux lignes."]), (0.2, 1.0)

def c_compliment():
    a = p(["Ta présentation tout à l'heure", "Ton discours au mariage", "Ton gâteau de ce midi", "Ta façon de gérer le client relou",
           "Ton dessin"])
    b = p(["c'était clair, posé, et t'as géré la question piège comme une pro.", "c'était sincère et drôle, tout le monde en parle encore.",
           "j'en rêve encore, je veux la recette ou un deuxième.", "chapeau, j'aurais explosé en deux minutes.",
           "franchement, ça mérite un cadre."])
    return f"{a}, {b} {p(['Bravo.', 'Respect.', '👏', 'Fier de toi.', ''])}".strip(), p(
        ["Compliment sincère et précis, chaleureux.", "Bienveillance bien écrite, statut généreux.",
         "Encouragement concret qui fait plaisir."]), (0.1, 0.9)

def c_triplet():
    a = p(["Café tiède", "Pluie fine", "Dimanche lent", "Fenêtre ouverte", "Pain chaud", "Vélo, vent"])
    b = p(["playlist parfaite", "chat sur les genoux", "livre entamé", "ville endormie", "odeur de lessive"])
    c = p(["Le mardi a ses charmes.", "Je ne demande rien de plus.", "Petit bonheur validé.", "On appelle ça la paix.",
           "Le luxe, c'est ça."])
    emo = p(["", " ☕", " 🌧️", " 🍃", ""])
    return f"{a}, {b}. {c}{emo}", p(["Petite phrase rythmée et douce, joli sens du détail.",
                                    "Caption Instagram simple mais élégante.",
                                    "Rythme ternaire agréable, sans grande profondeur."]), (0.3, 1.0)

def c_refus():
    a = p(["Merci pour l'invitation,", "Trop gentil d'avoir pensé à moi,", "Ça me touche que tu proposes,"])
    b = p(["mais ce soir je me choisis : plaid, soupe et silence.", "mais mon canapé m'a fait une scène hier, je lui dois une soirée.",
           "mais je suis en rendez-vous avec mon lit, et il est jaloux."])
    c = p(["Une prochaine ?", "On se rattrape vite.", "Bisous à tous.", "Gardez-moi une part."])
    return f"{a} {b} {c}", p(["Refus élégant et drôle, limites posées avec charme.",
                              "Dire non sans froisser : aura correcte.", "Légèreté et assurance tranquille."]), (0.3, 1.0)

def c_confiance():
    return p(["J'arrive. Garde-moi la meilleure chaise.", "Pas de panique, je gère. Je gère toujours.",
              "J'ai pas toutes les réponses, mais j'ai toujours une bonne question.",
              "Je me trompe parfois. Jamais deux fois de la même façon.",
              "Mets ta plus belle veste, on ne fait rien de spécial mais on le fait bien.",
              "Je ne sais pas danser, mais je sais très bien faire semblant.",
              "Je suis le genre d'ami qui ramène des glaçons et repart avec des secrets.",
              "Je te dois un café. Je paie toujours mes dettes, avec intérêts.",
              "On n'a pas raté le bus. On a gagné une balade."]), p(
        ["Confiance tranquille et formule bien tournée.", "Petite punchline efficace, charisme modéré.",
         "Assurance souriante, ni plus ni moins."]), (0.3, 1.0)

C_FIXED = [
    ("Je ne suis pas en retard, je laisse au suspense le temps de s'installer.", "Excuse spirituelle qui retourne la situation."),
    ("Mon superpouvoir : trouver la seule table au soleil en terrasse.", "Vantardise mignonne et légère."),
    ("Si tu cherches quelqu'un qui connaît toutes les paroles de Goldman, ta quête s'arrête ici.", "Accroche drôle et assumée."),
    ("Rien de tel qu'une balade sous la pluie pour se rappeler qu'on n'est pas en sucre.", "Petite philosophie du quotidien plaisante."),
    ("J'ai planté des tomates. Elles poussent. Je me sens comme un dieu mineur.", "Autodérision lumineuse."),
    ("La vie est trop courte pour boire du mauvais café et répondre aux mails le dimanche.", "Maxime légère et sympathique."),
    ("Ce soir, je cuisine. Venez affamés et indulgents.", "Invitation chaleureuse avec une pointe d'humour."),
    ("Je ne fais pas de bilan de fin d'année. Je fais des listes de choses à recommencer.", "Optimisme bien formulé."),
    ("Tu as le droit d'être fatigué. Tu n'as pas le droit d'oublier que tu es génial.", "Encouragement tendre et efficace."),
    ("Voyager léger : un sac, un carnet, et zéro regret.", "Bio de voyage simple et rythmée."),
    ("Moi aussi je me perds parfois. Mais je me perds toujours dans de jolis endroits.", "Tournure gracieuse et rassurante."),
    ("Je collectionne les cartes postales que je n'envoie jamais. Un jour, je t'en enverrai une.", "Détail intime et charmant."),
    ("Premier jour au nouveau job : j'ai retenu trois prénoms et l'emplacement de la machine à café. L'essentiel.", "Humour professionnel bien dosé."),
    ("Je préfère les gens qui rient fort à ceux qui parlent fort.", "Préférence affirmée avec finesse."),
    ("Note à moi-même : arrêter de m'excuser d'exister. Commencer par ce message.", "Prise de confiance touchante."),
]
def c_fixed():
    t, j = p(C_FIXED); return t, j, (0.0, 1.0)

# ---------------------------------------------------------------- FORTE AURA
FA_SENT = [
    "Je ne suis pas venu pour la fête, je suis venu parce que je savais que tu t'ennuierais sans quelqu'un pour te contredire.",
    "Je lis les gens mieux que les cartes.",
    "On m'a souvent dit que j'étais trop : trop calme, trop direct, trop absent. Je n'ai jamais démenti.",
    "Je ne fais pas de promesses, je fais des réservations.",
    "La ville s'éteignait fenêtre après fenêtre, et je comptais les lumières comme on compte ses regrets : lentement.",
    "J'ai appris à partir sans claquer la porte. Le silence fait plus de bruit.",
    "Tu peux m'appeler quand tu veux. Je ne décrocherai peut-être pas, mais tu sauras que je t'ai entendu.",
    "Je n'ai pas besoin d'avoir raison, j'ai besoin d'avoir été clair.",
    "Ce n'est pas de l'arrogance, c'est de l'expérience qui se tient droite.",
    "Je garde mes amis comme on garde les bons livres : peu nombreux, souvent relus.",
    "Je ne cherche pas l'attention. Elle me trouve, puis elle repart un peu changée.",
    "J'ai cessé de courir après les trains ; il en passe toujours un autre, et parfois c'est le bon.",
    "Mes meilleures idées naissent à deux heures du matin, mes meilleures décisions à neuf heures.",
    "Je préfère un non franc à un peut-être qui traîne.",
    "Il y a des gens qui remplissent une pièce. Moi, je la fais respirer.",
]
def fa_prose():
    s = R.sample(FA_SENT, R.choice([1, 2, 2]))
    t = " ".join(s)
    return t, p(["Assurance calme et formules nettes, charisme réel.",
                 "Voix posée, phrases ciselées, aura bien installée.",
                 "Dominance tranquille et un soupçon de mystère."]), (0.2, 1.0)

def fa_bio():
    a = p(["Je cuisine mieux que je ne promets.", "Je parle trois langues et je les utilise surtout pour me taire.",
           "Photographe de ce que les autres ne regardent pas.", "Grand lecteur, petit dormeur.",
           "Je connais les bons bars et les mauvaises excuses."])
    b = p(["Écris-moi si tu sais tenir une conversation après minuit.", "Viens avec une histoire, je fournis le vin.",
           "Je ne swipe pas, je choisis.", "Les gens pressés peuvent continuer de défiler.",
           "Je réponds lentement, mais je réponds vraiment."])
    emo = p(["", " 🌒", " 🥃", " 📷", ""])
    return f"{a} {b}{emo}", p(["Bio sélective et assurée, attractive par la retenue.",
                               "Exigence élégante, personnalité affirmée.",
                               "Charisme sobre qui donne envie d'écrire."]), (0.2, 1.0)

def fa_couplet():
    C = [
        "Je pars sans bruit, je pars sans haine,\nLe vent connaît ma rue lointaine.",
        "J'ai rangé mes peurs dans un tiroir,\nEt j'ai gardé la clé du soir.",
        "Tu m'as cherché dans la cohue,\nJ'étais l'ombre au coin de la rue.",
        "Ne me demande pas où je vais :\nJe n'y suis jamais allé, mais je le sais.",
        "Je marche seul, mais pas perdu,\nCar chaque pas m'est dû.",
        "La nuit m'écrit des lettres brèves,\nJe lui réponds avec mes rêves.",
        "J'ai le sourire des gens tranquilles\nEt le regard des grandes villes.",
        "On m'a dit : reste, j'ai dit : peut-être,\nPuis j'ai ouvert grand la fenêtre.",
        "Je bois mon café sans sucre et sans hâte,\nLe monde attendra que je me batte.",
        "Je n'ai pas de carte, pas de boussole,\nJuste un cœur qui jamais ne s'affole.",
        "Je laisse aux autres le bruit des fêtes,\nMoi je préfère les tempêtes.",
        "Ton nom flotte encore dans l'escalier,\nMais j'ai appris à l'oublier.",
    ]
    return p(C), p(["Rimes simples mais assurées, posture séduisante.",
                    "Petite musique en octosyllabes, charisme doux.",
                    "Forme rimée et image nette, belle présence."]), (0.3, 1.0)

def fa_rupture():
    a = p(["Je te souhaite sincèrement d'être heureux.", "Je ne t'en veux pas.", "Merci pour ces deux ans.",
           "Je pars sans colère."])
    b = p(["Juste plus avec moi.", "J'ai simplement fini de t'attendre.", "Le reste, je le garde pour moi.",
           "On ne se doit plus rien, et c'est très bien."])
    c = p(["Garde le pull, il t'allait mieux qu'à moi.", "Les clés sont sous le paillasson.", "Arrose la plante, elle n'y est pour rien.",
           "Ne me réponds pas, ce message n'est pas une question."])
    return f"{a} {b} {c}", p(["Rupture digne et tranchante, maîtrise totale.",
                              "Élégance dans la fin, statut intact.",
                              "Détachement classe avec un détail qui frappe."]), (0.3, 1.0)

def fa_charme():
    a = p(["Tu as ri à ma blague la plus nulle.", "Tu m'as volé mon briquet hier soir.", "Tu as oublié ton écharpe chez moi.",
           "Tu as gagné au billard, je l'admets."])
    b = p(["Je considère ça comme un contrat.", "Je compte me venger autour d'un dîner.",
           "Je la garde en otage jusqu'à vendredi, 20h.", "La revanche se joue en tête-à-tête."])
    return f"{a} {b}", p(["Rizz assuré et joueur, initiative élégante.", "Drague maîtrisée, humour et aplomb.",
                          "Charme direct sans lourdeur."]), (0.3, 1.0)

FA_FIXED = [
    ("Je n'ai pas toujours eu raison, mais je n'ai jamais tremblé en me trompant.", "Assurance philosophique bien frappée."),
    ("Il pleut sur Paris comme il pleut dans les films : exprès, pour que quelqu'un coure vers quelqu'un.", "Image cinématographique charmante."),
    ("Je ne demande pas la permission d'être là. Je demande juste où sont les verres.", "Dominance décontractée et drôle."),
    ("On n'oublie pas les gens qui écoutent vraiment. Alors parle, je t'écoute.", "Présence magnétique par l'écoute."),
    ("Mon silence n'est pas un vide. C'est une pièce meublée où tu n'es pas encore invité.", "Métaphore de mystère bien construite."),
    ("Ce soir la mer est calme, et moi aussi. Ça n'arrive pas souvent aux deux en même temps.", "Mélancolie sereine et élégante."),
    ("Je ne fuis pas les conflits. Je les laisse simplement s'épuiser contre mon calme.", "Statut affirmé, ton maîtrisé."),
    ("J'aime les gens qui arrivent en avance et repartent en dernier : ils savent ce que vaut une soirée.", "Observation fine et distinguée."),
    ("Tu as quitté la soirée tôt. La soirée aussi, du coup.", "Compliment indirect et habile."),
    ("Mes plans B ont des plans B. Mais mon plan A, c'est toi.", "Rizz à chute bien construite."),
]
def fa_fixed():
    t, j = p(FA_FIXED); return t, j, (0.0, 1.0)

# ---------------------------------------------------------------- ALEXANDRINS
# familles de rimes : (genre, [vers de 12 syllabes])
FAM = {
    "uit": ("m", ["Je marche sans flambeau dans le cœur de la nuit,",
                  "Et l'ombre me salue, et l'ombre aussitôt fuit.",
                  "Le monde fait silence où mon pas le poursuit,",
                  "Et chaque étoile éteinte est un feu qui me suit."]),
    "er": ("m", ["Je porte sur le front la couronne d'hiver,",
                 "Et nul n'a su briser ce qui chez moi est fer.",
                 "Mon silence a le poids d'un royaume désert,",
                 "Et mon regard tranquille est un livre entrouvert."]),
    "ant": ("m", ["Je ne m'incline pas devant l'ordre du temps,",
                  "Je l'écoute passer comme on écoute un chant.",
                  "Les empires sont morts, je demeure pourtant,",
                  "Plus calme que la pierre et plus vif que l'instant."]),
    "ois": ("m", ["J'ai vu tomber les tours et s'effacer les rois,",
                  "Et j'ai gardé pour moi le secret de leur voix.",
                  "Je parle rarement, mais on m'entend parfois",
                  "Comme on entend la neige au silence des bois."]),
    "ere": ("f", ["J'ai bu tous les adieux comme on boit l'eau amère,",
                  "Et j'ai gardé du sel au creux de ma colère.",
                  "Je n'ai jamais prié qu'une seule lumière,",
                  "Et c'est elle qui brûle au fond de ma paupière."]),
    "oire": ("f", ["Je ne réclame pas qu'on chante mon histoire,",
                   "Le vent la redira bien mieux que ma mémoire.",
                   "J'ai laissé dans la cendre un reste de victoire,",
                   "Comme on laisse une rose au bord d'une écritoire."]),
    "ame": ("f", ["Il suffit d'un regard pour réveiller mon âme,",
                  "Et la foule se tait sous l'éclat de ma flamme.",
                  "On murmure mon nom comme on murmure un drame,",
                  "Et tout cœur un peu las le relit et l'acclame."]),
    "ure": ("f", ["Je porte mes chagrins comme on porte une armure,",
                  "Et le temps, à mes pieds, dépose sa blessure.",
                  "Nul n'a jamais compris ma tranquille écriture,",
                  "Car j'écris sans un mot, à même la nature."]),
}
MASC = [k for k, v in FAM.items() if v[0] == "m"]
FEM = [k for k, v in FAM.items() if v[0] == "f"]

def fix_end(lines):
    out = [l for l in lines]
    out[-1] = out[-1].rstrip(",.;:") + "."
    for i in range(len(out) - 1):
        out[i] = out[i].rstrip(".") + ("," if not out[i].endswith((",", ";", ":")) else "")
    return out

def pair(fam):
    L = FAM[fam][1]
    i = R.choice([0, 2]) if R.random() < 0.7 else R.choice([0, 1, 2])
    return [L[i], L[i + 1]] if i + 1 < len(L) else [L[i - 1], L[i]]

def quatrain():
    f, m = p(FEM), p(MASC)
    a, b = pair(f), pair(m)
    scheme = p(["ABAB", "AABB", "ABBA"])
    if scheme == "ABAB": L = [a[0], b[0], a[1], b[1]]
    elif scheme == "AABB": L = [a[0], a[1], b[0], b[1]]
    else: L = [a[0], b[0], b[1], a[1]]
    return fix_end(L), scheme

def l_quatrain():
    L, sch = quatrain()
    return "\n".join(L), p([f"Quatrain d'alexandrins en rimes {'croisées' if sch=='ABAB' else 'plates' if sch=='AABB' else 'embrassées'}, majesté et mystère.",
                            "Alexandrins rimés qui imposent une présence souveraine.",
                            "Forme classique maîtrisée et voix dominante."]), (0.3, 1.0)

def l_distique():
    f = p(list(FAM))
    a = pair(f)
    pre = p(["", "", "Statut du jour :\n", "Écrit sur la buée :\n"])
    return pre + "\n".join(fix_end(a)), p(["Distique d'alexandrins rimés, sobre et marquant.",
                                           "Deux vers parfaits qui suffisent à tenir la pièce.",
                                           "Rime riche et rythme ample en format court."]), (0.0, 0.7)

LEG_SENT = [
    "Il est trois heures du matin et la lune a pris ta place à la fenêtre ; elle fait moins de bruit, mais elle brille moins.",
    "Je garde de chaque ville un peu de pluie dans mes poches.",
    "Je ne cours après personne ; je laisse le temps trier ceux qui méritent de me rattraper.",
    "On me dit froid. Je suis seulement précis.",
    "J'ai rangé mes colères dans un tiroir que je n'ouvre plus, mais dont je garde la clé.",
    "Je parle peu, mais je n'ai jamais rien dit pour rien.",
    "Certains collectionnent les gens ; moi, je collectionne les silences qui valent la peine.",
    "J'écris tes initiales sur la buée, et je laisse le soleil décider.",
    "Je ne suis pas en retard : je suis arrivé quand ça devenait intéressant.",
    "Je pars toujours avant la fin du film ; je préfère imaginer la mienne.",
    "On a essayé de me résumer ; il a fallu un deuxième tome.",
    "Le vent connaît mon prénom, et il ne le répète à personne.",
    "Je ne gagne pas les disputes, je les rends inutiles.",
    "Je laisse derrière moi des portes entrouvertes et des parfums qui posent des questions.",
    "J'ai un faible pour les gares, les orages et les gens qui tiennent parole.",
    "J'ai traversé des déserts pour des raisons que j'ai oubliées ; je garde de chacun un peu de sable et beaucoup de silence.",
    "Je ne promets pas la lune, je t'apprends à la voir.",
    "Mes cicatrices racontent mieux que moi, alors je les laisse parler.",
]
def l_prose():
    s = R.sample(LEG_SENT, R.choice([2, 2, 3]))
    emo = p(["", "", " 🌒", " 🕯️", ""])
    return " ".join(s) + emo, p(["Prose aphoristique, mystère et dominance au sommet.",
                                 "Formules ciselées qui installent une légende.",
                                 "Élégance, retenue et images inattendues."]), (0.2, 1.0)

L_FIXED = [
    ("Je suis le calme qui précède, et parfois celui qui suit. Rarement la tempête : je n'en ai pas besoin.", "Maîtrise absolue exprimée avec poésie."),
    ("J'ai aimé comme on allume un phare : pour les autres, sans jamais quitter ma falaise.", "Métaphore puissante et solitude souveraine."),
    ("Ne me cherche pas dans la foule ; cherche l'endroit où la foule s'écarte.", "Présence magnétique en une image."),
    ("Je n'ai pas oublié. J'ai pardonné, ce qui est beaucoup plus cruel.", "Retournement sec et redoutable."),
    ("Ma mère disait que j'avais des yeux de veille d'orage. Elle avait raison : on les regarde toujours avant de sortir.", "Récit intime et imagerie saisissante."),
    ("La mer n'a jamais demandé pardon au rivage. Elle revient, simplement, et c'est sa façon d'aimer.", "Image marine d'une grande élégance."),
    ("J'écris à l'encre lente, celle qui sèche après les promesses.", "Formule raffinée et mystérieuse."),
    ("Tu voulais une réponse ; je t'ai donné une énigme. Tu y penses encore, avoue.", "Mystère joueur et emprise douce."),
]
def l_fixed():
    t, j = p(L_FIXED); return t, j, (0.0, 1.0)

# ---------------------------------------------------------------- AURA DIVINE
DIV_SENT = [
    "Je ne suis pas entré dans la pièce : c'est la pièce qui s'est réorganisée autour de moi.",
    "Les tempêtes ne crient pas ; elles arrivent.",
    "J'ai appris le silence auprès des cathédrales, et la patience auprès des fleuves.",
    "Ceux qui m'ont oublié rêvent encore de moi, et c'est leur seule pénitence.",
    "Je porte mon passé comme un manteau de velours : sans le montrer, mais sans jamais avoir froid.",
    "Le monde m'a offert ses couronnes ; je les ai posées au bord du chemin pour que les enfants jouent avec.",
    "On ne me cherche pas. On me reconnaît.",
    "La nuit me tutoie depuis l'enfance.",
    "Je n'ai jamais gagné de guerre ; j'ai simplement fait en sorte qu'elles n'osent pas commencer.",
    "Mon nom ne se crie pas, il se murmure, et c'est pour cela qu'il dure.",
    "J'ai bâti des villes avec des phrases et je les ai rendues au vent sans rien demander.",
    "Il y a dans mon calme quelque chose que les orages envient.",
    "Quand je me tais, les horloges hésitent.",
    "Je ne demande pas qu'on m'aime : je demande qu'on soit à la hauteur de ce qu'on ressent.",
    "Je sais attendre comme attendent les montagnes, c'est-à-dire sans jamais douter.",
    "Les étoiles ne se comparent pas entre elles ; elles brûlent, et c'est assez.",
    "J'ai traversé l'hiver sans manteau, et c'est l'hiver qui s'en souvient.",
    "Je n'ai pas de secrets : j'ai des profondeurs.",
    "Chaque porte que l'on m'a fermée est devenue une fenêtre sur la mer.",
    "On a voulu m'éteindre ; on n'a fait qu'apprendre au feu mon adresse.",
]
def d_prose():
    s = R.sample(DIV_SENT, R.choice([3, 3, 4]))
    return " ".join(s), p(["Monologue mythique : mystère, dominance et beauté à leur zénith.",
                           "Chaque phrase est une sentence gravée dans le marbre.",
                           "Souveraineté absolue servie par des images cosmiques."]), (0.2, 1.0)

TITLES = ["Nocturne", "Le Veilleur", "Souveraineté", "Épitaphe pour un vivant", "Ce que dit la pierre", "Hiver royal",
          "L'Absent", "Cantique de l'ombre", "Testament du soir", "Le Phare", "Ode au silence", ""]
def d_poeme():
    fs = R.sample(FEM, 2) if R.random() < 0.5 else [p(FEM)]
    ms = R.sample(MASC, 2) if len(fs) == 1 else [p(MASC)]
    fams = fs + ms
    R.shuffle(fams)
    blocks = []
    if len(fams) == 3:
        # sizain : AAB CCB style simplifié -> trois distiques plats
        for f in fams: blocks += pair(f)
        L = fix_end(blocks)
    else:
        L = fix_end(blocks)
    # parfois deux quatrains
    if R.random() < 0.35:
        q1, _ = quatrain(); q2, _ = quatrain()
        if not set(q1) & set(q2):
            L = fix_end(q1) + [""] + fix_end(q2)
    title = p(TITLES)
    t = (f"« {title} »\n\n" if title else "") + "\n".join(L)
    return t, p(["Poème en alexandrins rimés, majesté classique et mystère total.",
                 "Rimes alternant féminin et masculin, souffle épique impeccable.",
                 "Musicalité parfaite et voix souveraine : divin."]), (0.2, 1.0)

def d_aphorisme():
    return p(["Je n'élève jamais la voix. Les tempêtes non plus ne crient pas : elles arrivent.",
              "On m'a promis l'éternité ; j'ai demandé qu'on me laisse d'abord le soir.",
              "Je ne suis pas une réponse. Je suis la question qu'on emporte en rentrant.",
              "J'ai dormi sous des ciels que personne n'a encore nommés.",
              "Tout passe. Moi, je reste juste assez longtemps pour qu'on s'en souvienne.",
              "Je ne frappe pas aux portes ; elles s'ouvrent au bruit de mes pensées.",
              "Le temps m'a demandé conseil. Je lui ai dit de ne pas se presser.",
              "Je ne brille pas : j'éclaire, et la différence se voit dans le noir.",
              "La mer m'a appris qu'on peut tout reprendre sans jamais rien voler."]), p(
        ["Aphorisme parfait, densité maximale en une ligne.", "Mystère cosmique et autorité absolue.",
         "Sentence brève qui laisse un silence divin."]), (0.0, 0.9)

D_FIXED = [
    ("Je suis né un soir où la pluie hésitait. Depuis, elle me demande la permission avant de tomber. Les rois ont des gardes ; moi, j'ai des saisons qui m'attendent. Et quand je partirai, ce ne sera pas une absence : ce sera une marée basse, et tout le monde saura que je reviens.",
     "Monologue mythologique d'une ampleur et d'une beauté rares."),
    ("« Sonnet tronqué »\n\nJe marche sans flambeau dans le cœur de la nuit,\nJe porte sur le front la couronne d'hiver ;\nMon silence a le poids d'un royaume désert,\nEt chaque étoile éteinte est un feu qui me suit.",
     "Alexandrins embrassés d'une majesté hivernale."),
    ("Tu me demandes qui je suis. Demande plutôt à la neige ce qu'elle a vu, aux phares ce qu'ils ont gardé, aux villes ce qu'elles taisent quand les fêtes sont finies. Je suis ce qu'il reste quand tout le monde est parti : la lumière qui ne s'éteint pas parce qu'elle n'a jamais demandé à être allumée.",
     "Crescendo poétique et identité cosmique, aura absolue."),
    ("Ils ont écrit mon nom sur le sable ; la mer l'a appris par cœur.", "Image d'une perfection lapidaire."),
    ("Je ne marche pas sur l'eau. Je lui demande simplement de se tenir droite quand je passe.", "Dominance surnaturelle avec une élégance tranquille."),
]
def d_fixed():
    t, j = p(D_FIXED); return t, j, (0.0, 1.0)

# ---------------------------------------------------------------- ASSEMBLAGE
CLASSES = [
    ("Anti-Aura", -100, -41, [(a_relance, 3), (a_bio, 3), (a_grind, 2), (a_jalousie, 2), (a_poeme, 2), (a_approche, 2), (a_spam, 2), (a_fixed, 4)]),
    ("Aura Faible", -40, -11, [(f_hesitant, 3), (f_bio, 2), (f_excuse, 2), (f_linkedin, 2), (f_poeme_plat, 2), (f_mystere, 2), (f_vocal, 1), (f_fixed, 3)]),
    ("Aura Neutre", -10, 4, [(n_logistique, 3), (n_courses, 2), (n_transport, 2), (n_bio, 2), (n_avis, 2), (n_meteo, 1), (n_mail, 2), (n_fixed, 3)]),
    ("Aura Correcte", 5, 24, [(c_humour, 3), (c_bio, 3), (c_compliment, 2), (c_triplet, 2), (c_refus, 1), (c_confiance, 2), (c_fixed, 3)]),
    ("Forte Aura", 25, 49, [(fa_prose, 4), (fa_bio, 3), (fa_couplet, 2), (fa_rupture, 2), (fa_charme, 2), (fa_fixed, 2)]),
    ("Aura Légendaire", 50, 74, [(l_quatrain, 4), (l_distique, 2), (l_prose, 5), (l_fixed, 1)]),
    ("Aura Divine", 75, 100, [(d_prose, 4), (d_poeme, 5), (d_aphorisme, 1), (d_fixed, 1)]),
]

rows = []
seen = set()
for name, lo, hi, gens in CLASSES:
    fns = [g for g, w in gens for _ in range(w)]
    count, tries = 0, 0
    per_fn = {}
    while count < 200 and tries < 50000:
        tries += 1
        fn = p(fns)
        text, just, (flo, fhi) = fn()
        if text in seen:
            continue
        # évite qu'un générateur à liste fixe ne monopolise
        cap = 30 if fn.__name__.endswith("fixed") or fn.__name__ in ("c_confiance", "d_aphorisme", "fa_couplet") else 999
        if per_fn.get(fn.__name__, 0) >= cap:
            continue
        seen.add(text)
        per_fn[fn.__name__] = per_fn.get(fn.__name__, 0) + 1
        span = hi - lo
        score = round(lo + span * (flo + (fhi - flo) * R.random()))
        rows.append((text, name, max(lo, min(hi, score)), just))
        count += 1
    print(name, count, per_fn)

R.shuffle(rows)
with open("aura_dataset.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerow(["texte", "classe", "score", "justification"])
    w.writerows(rows)
print(len(rows))
