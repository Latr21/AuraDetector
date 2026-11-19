import random, csv
from collections import Counter, defaultdict

R = random.Random(67)
p = R.choice
def S(pool, k): return R.sample(pool, k)

CLASSES = [("Anti-Aura", -100, -41), ("Aura Faible", -40, -11), ("Aura Neutre", -10, 4), ("Aura Correcte", 5, 24),
           ("Forte Aura", 25, 49), ("Aura Légendaire", 50, 74), ("Aura Divine", 75, 100)]
W = dict(R=0.30, S=0.20, O=0.15, B=0.15, M=0.10, P=0.10)
def cls_of(s):
    for n, lo, hi in CLASSES:
        if lo <= s <= hi: return n
    return None

# biais de composantes par style
OFF = {
    "brainrot":  dict(R=5, S=0, O=18, B=-8, M=-5, P=-12),
    "politique": dict(R=5, S=15, O=-10, B=5, M=-8, P=-5),
    "moderne":   dict(R=10, S=-3, O=0, B=-5, M=0, P=-12),
    "prose":     dict(R=-10, S=-8, O=-5, B=18, M=12, P=18),
    "hybride":   dict(R=0, S=0, O=15, B=5, M=0, P=10),   # brainrot en alexandrins
}

def typo(t, prob=0.6):
    for a, b in [("c'est", "cé"), ("je suis", "jsuis"), ("pourquoi", "pk"), ("vraiment", "vrmt"), ("quoi", "koi"),
                 ("je sais pas", "jsp"), ("tout le monde", "tlm"), ("quand même", "qd mm"), ("toujours", "tjr")]:
        if a in t and R.random() < prob: t = t.replace(a, b)
    return t

# ============================================================ POLITIQUE
# Archétypes oratoires (aucun nom réel) : jup = jupitérien/technocrate, trib = tribun insoumis,
# nat = souverainiste "bon sens", jpm = jeune Premier ministre "méthode", ord = ministre de l'ordre,
# cent = centriste béarnais, norm = flegmatique normand, rep = député-reporter populaire
TOP_OPEN = {
    "jup": ["Mes chers compatriotes.", "Je veux vous parler ce soir avec gravité, et en même temps avec espérance."],
    "trib": ["Mes amis, regardez-vous !", "Ils pensaient que nous étions fatigués. Ils se sont trompés de peuple."],
    "nat": ["Françaises, Français, je vous ai entendus.", "Ce soir, je ne vous parle pas des partis. Je vous parle de vous."],
    "jpm": ["Je vais vous dire les choses simplement.", "J'ai une méthode, et elle tient en un mot : agir."],
    "ord": ["Je vais être très clair.", "Il y a des soirs où un ministre doit parler peu et parler net."],
    "cent": ["Je le dis depuis longtemps, et je le redis ce soir avec la tranquillité de ceux qui ont eu raison trop tôt.",
             "Il y a, dans ce pays, une majorité silencieuse qui ne demande qu'une chose : qu'on se parle."],
    "norm": ["Je ne vais pas vous faire de grand discours.", "Je vais vous dire ce qui est, ce qui sera, et ce que cela coûtera."],
    "rep": ["Hier, j'étais dans la Somme, devant une usine qui ferme.",
            "Avant de venir dans cet hémicycle doré, je suis allé voir ceux qui ne viendront jamais ici."],
}
TOP_BODY = [
    "La France n'a jamais été aussi grande que lorsqu'elle a refusé d'être petite.",
    "L'histoire ne frappe pas à la porte : elle l'enfonce.",
    "Je ne vous promets pas que ce sera facile ; je vous promets que ce sera juste.",
    "Il n'y aura pas un mètre carré de la République où la loi devra demander la permission d'entrer.",
    "Ce pays ne se gouverne pas contre une moitié de lui-même.",
    "Les Français sont des adultes : il est temps de leur parler comme à des adultes.",
    "Une aide-soignante m'a dit : on ne demande pas des médailles, on demande du temps. Cette phrase pèse plus lourd que tous vos rapports.",
    "Le courage, ce n'est pas de crier plus fort ; c'est de tenir quand plus personne ne regarde.",
    "Nous ne sommes pas les héritiers d'une défaite, nous sommes les ancêtres d'une victoire.",
    "Je ne vous demande pas de me croire. Je vous demande de me regarder faire.",
    "Le peuple, quand il se lève, ne demande la permission à personne.",
    "La main tendue n'est pas une main faible.",
    "On ne gouverne pas avec des sondages, on gouverne avec une boussole.",
    "Ceux qui se lèvent tôt n'ont pas besoin qu'on les flatte ; ils ont besoin qu'on les respecte.",
]
TOP_CLOSE = ["Vive la République, et vive la France.", "Au travail.", "Le reste, c'est vous qui l'écrirez.", "Merci.",
             "Nous y arriverons. Ensemble.", "Et cette fois, personne ne nous fera reculer."]

def pol_divine():
    a = p(list(TOP_OPEN)); t = " ".join([p(TOP_OPEN[a])] + S(TOP_BODY, 2) + [p(TOP_CLOSE)])
    t += p(["", "\n[standing ovation de quatre minutes]", "\n[silence total, puis la salle se lève]", ""])
    return t, p(["Discours souverain : rythme, gravité et formules historiques.",
                 "Effets oratoires parfaitement dosés, la salle est tenue.",
                 "Charisme d'estrade et autorité naturelle, niveau manuel d'histoire."])

def pol_legend():
    a = p(list(TOP_OPEN)); t = " ".join([p(TOP_OPEN[a]), p(TOP_BODY), p(TOP_CLOSE)])
    return t, p(["Prise de parole dense et dominante, une formule qui reste.",
                 "Ton présidentiel maîtrisé, punchline mémorable.",
                 "Tribune efficace qui impose le respect."])

DEBAT_PUNCH = [
    "Vous avez des fiches, j'ai des convictions.",
    "Vous parlez des Français ; moi, je leur parle.",
    "Vous avez eu cinq ans pour le faire. J'ai cinq minutes, et elles suffiront.",
    "Je ne suis pas venu ici pour être aimé, je suis venu pour être utile.",
    "Vous confondez l'autorité et le bruit. Moi, je baisse la voix, et vous m'écoutez.",
    "Gardez vos leçons, je garde mes résultats.",
    "Vous citez des chiffres, je cite des visages.",
    "Le jour où vous aurez une idée, prévenez-moi : je vous céderai la parole avec plaisir.",
]
def pol_debat():
    ctx = p(["[débat de l'entre-deux-tours] ", "[Questions au gouvernement] ", "[plateau TV, 20h] ", "[réplique en commission] ", ""])
    t = ctx + " ".join(S(DEBAT_PUNCH, R.choice([1, 2])))
    return t, p(["Réplique de débat cinglante, dominance verbale.", "Punchline politique qui retourne l'adversaire.",
                 "Aplomb et sens du timing en plateau."])

def pol_terrain():
    a = p(["Belle rencontre ce matin avec les agriculteurs de la Beauce.", "Visite d'une PME de robotique à Grenoble.",
           "Échange franc avec les soignants de l'hôpital de Rodez.", "Marché de Brive ce dimanche.",
           "Inauguration de la nouvelle médiathèque de Lens."])
    b = p(["Écouter, comprendre, agir.", "On ne lâche rien.", "La France qui travaille, c'est elle.",
           "Merci pour l'accueil et la franchise.", "Les solutions viennent du terrain."])
    return f"{a} {b} {p(['🇫🇷', '💪', '', '#territoires', '🌾'])}".strip(), p(
        ["Tweet de terrain propre et positif, sans grand relief.", "Communication politique correcte et lisse.",
         "Message rassurant, charisme modéré."])

def pol_neutre():
    return p([
        f"Le Conseil des ministres s'est réuni ce mercredi. Le projet de loi relatif à {p(['la simplification administrative', 'la sobriété énergétique', 'la sécurité routière', 'la fonction publique territoriale'])} a été présenté.",
        f"Amendement n°{R.randint(12, 2400)} : à l'alinéa {R.randint(2, 9)}, remplacer le mot « {p(['peut', 'doit', 'notamment', 'annuel'])} » par le mot « {p(['doit', 'peut', 'en particulier', 'pluriannuel'])} ».",
        f"Le ministre se rendra {p(['jeudi', 'vendredi', 'lundi'])} à {p(['Lyon', 'Lille', 'Metz', 'Pau', 'Brest'])} pour une visite consacrée à {p(['l’apprentissage', 'la rénovation énergétique', 'la sécurité du quotidien', 'l’accès aux soins'])}.",
        f"La séance est suspendue. Elle reprendra à {p(['21h30', '15h', '17h45', '10h'])}.",
        f"Ordre du jour de la commission : audition du directeur général de {p(['l’Insee', 'la DGFiP', 'Météo-France', 'l’ANSSI'])}.",
        f"Le scrutin est ouvert. {R.randint(400, 577)} votants, {R.randint(200, 350)} voix pour. Le texte est adopté.",
    ]), p(["Communiqué institutionnel, aucune aura.", "Langage administratif strictement neutre.", "Procédure parlementaire sans charge émotionnelle."])

LOW_OPEN = {
    "jup": "Alors, je vais être très clair, et en même temps un peu flou, parce que la clarté, profondément, c'est aussi du flou.",
    "trib": "Je suis la voix du peuple ! Enfin, c'est surtout moi qui parle. TAISEZ-VOUS, je n'ai pas fini ma phrase de 47 minutes !",
    "nat": "Mes chers compatriotes, le bon sens, c'est le bon sens. Et le bon sens, il est sensé.",
    "jpm": "J'ai une méthode, c'est la méthode. J'ai même fait un PowerPoint avec le mot « méthode » en gras.",
    "ord": "Tolérance zéro ! Fermeté totale ! J'ai d'ailleurs fermement décidé de m'acheter une trottinette.",
    "cent": "Je le dis depuis trente ans. Personne n'écoutait il y a trente ans. Personne n'écoute aujourd'hui.",
    "norm": "Écoutez, je suis calme. Tellement calme que je me suis endormi pendant ma propre conférence de presse.",
    "rep": "Hier j'ai rencontré Sandrine. Avant-hier aussi. Je crois qu'elle commence à avoir peur.",
}
LOW_BODY = [
    "La question est complexe, et la complexité appelle des réponses, des réponses qui doivent être, comment dire, des réponses.",
    "Nous allons lancer une grande concertation pour préparer le lancement d'une consultation sur la méthode de la concertation.",
    "Je n'ai pas lu le texte, mais je le combattrai avec la dernière énergie.",
    "Je tiens à remercier mon équipe, mon chauffeur, et le monsieur qui tient le micro, surtout lui.",
    "Les chiffres, je ne les ai pas sous les yeux, mais ils sont bons. Ou ils vont l'être. Ou ils l'étaient.",
    "Il faut renouer avec la confiance, et pour cela il faut d'abord renouer avec le renouement.",
    "Je ne réponds pas aux polémiques, sauf à celle-ci, et à la suivante, et à celle de demain.",
]
LOW_CLOSE = ["Voilà.", "Merci… ah, c'est déjà fini ? Bon.", "Je n'ai pas d'autre commentaire. Si, un dernier.", "Pas de questions ? Tant mieux.", "Vive la… pardon, j'ai perdu ma fiche."]

def pol_faible():
    a = p(list(LOW_OPEN)); t = " ".join([LOW_OPEN[a], p(LOW_BODY), p(LOW_CLOSE)])
    return t, p(["Langue de bois et tics oratoires qui tournent à vide.", "Discours poussif qui s'auto-sabote.",
                 "Grandiloquence sans substance, salle qui décroche."])

def pol_anti():
    a = p([
        "Mes chers compatriotes, ce soir je vous annonce le plan Skibidi 2030 : chaque Français recevra mille points d'aura.",
        "Françaises, Français, j'ai décidé de faire un dab devant les caméras pour parler à la jeunesse.",
        "Mes amis ! Le peuple veut du rizz ! Et le rizz, c'est moi ! Enfin, c'est nous ! Enfin, laissez-moi finir !",
        "Je vais être très ferme : la fanum tax sera désormais prélevée à la source.",
        "Chers jeunes, je suis comme vous : sigma, Ohio, gyatt. J'ai demandé à mon stagiaire, il m'a dit que c'était bien.",
        "Mesdames et Messieurs les députés, je propose d'inscrire le 6-7 dans la Constitution.",
    ])
    b = p(["Personne n'a applaudi.", "[le micro coupe]", "Le stagiaire a démissionné en direct.", "[rires gênés dans l'hémicycle]",
           "J'ai fait un mewing pendant la minute de silence.", "Ma propre équipe a quitté la salle."])
    c = p(["Vive la Ré… allô ? Le micro ?", "Je ne retire rien.", "C'était prévu.", "Je reviendrai. Plus fort. Plus skibidi.", "Merci, merci, ne vous levez pas, ah, vous partez."])
    return f"{a} {b} {c}", p(["Récupération du brainrot par un politique : malaise national.",
                              "Démagogie jeune ratée, aura détruite en direct.",
                              "Grandiloquence ridicule et tentative de buzz pathétique."])

# ============================================================ BRAINROT
BR_TOP = [
    "Il est entré sans un bruit, a payé la fanum tax de toute la tablée, et il est reparti sans prendre une seule frite.",
    "Son mewing est si constant que les sculpteurs de la Renaissance réclament des droits d'auteur.",
    "Il ne farm pas l'aura : l'aura vient se faire farmer d'elle-même, par respect.",
    "Quand il fait le 6-7, ses mains montent lentement, comme une balance qui rend la justice.",
    "Même les NPC de l'Ohio ont interrompu leur boucle pour le regarder passer.",
    "Elle n'a pas de rizz : elle a un droit de veto sur le rizz des autres.",
    "Le scuba, chez lui, n'est pas une danse ; c'est une plongée dans les abysses du charisme.",
    "Il a dabé une seule fois, en 2016, et le geste est resté suspendu dans l'air depuis.",
    "Les sigmas ont un code ; lui l'a écrit, puis il a oublié le mot de passe exprès.",
    "Il ne dit jamais « no cap ». Les casquettes tombent toutes seules quand il parle.",
    "Tralalero Tralala lui a demandé un autographe ; il a signé d'un simple regard.",
    "Bombardiro Crocodilo a fait demi-tour en voyant sa mâchoire à l'horizon.",
    "Il a regardé la caméra trois secondes, sans sourire, et l'algorithme l'a mis en page d'accueil de l'humanité.",
    "On dit qu'il a mogué un miroir, et que le miroir a demandé une revanche.",
]
BR_TAG_TOP = ["", "", " +∞ aura.", " 🗿", " Aura farming de niveau cosmique.", " Chat, is this real ?"]
def br_divine():
    return " ".join(S(BR_TOP, 3)) + p(BR_TAG_TOP), p(["Brainrot maîtrisé jusqu'au mythe : chaque référence est une légende.",
                                                      "Aura farming stoïque, absurde et parfaitement écrit.",
                                                      "Culture internet élevée au rang d'épopée."])
def br_legend():
    return " ".join(S(BR_TOP, 2)) + p(BR_TAG_TOP), p(["Brainrot raconté avec retenue et timing parfait.",
                                                      "Mythologie internet absurde mais classe.",
                                                      "Références maîtrisées et chute impeccable."])

HYB = [  # brainrot en alexandrins (genre, vers)
    ("J'ai mewé dans le noir jusqu'au lever du jour,", "Et l'Ohio tout entier m'a juré son amour."),
    ("Je ne fais pas le dab, je laisse le dab venir,", "Comme un vieux souverain qui n'a plus à courir."),
    ("Les NPC se sont tus quand j'ai franchi la porte,", "Car l'aura que je farme est d'une étrange sorte."),
    ("J'ai payé la fanum tax d'un geste de la main,", "Et la frite volée m'a dit : « Merci, demain. »"),
    ("Six, sept : mes mains ont dit ce que ma bouche tait,", "Et la classe a compris que le cours s'arrêtait."),
    ("Je plonge dans le scuba comme on plonge en la mer,", "Sans masque, sans bouteille, et sans un mot amer."),
]
def hyb():
    k = R.choice([1, 2])
    lines = [l for c in S(HYB, k) for l in c]
    title = p(["", "« Ode au mewing »\n", "« Sonnet de l'Ohio »\n", "« Complainte du sigma »\n"])
    return title + "\n".join(lines), p(["Brainrot en alexandrins rimés : absurde et forme classique fusionnent.",
                                        "Rimes plates et références internet, originalité maximale.",
                                        "Musicalité classique au service du brainrot, effet divin."])

def br_forte():
    a = p(["Frérot", "Le nouveau de la classe", "Ma daronne", "Le prof de philo", "Le chauffeur du 72", "Mon grand-père"])
    b = p(["a fait le 6-7 pile quand la prof de maths a dit « page 67 »", "a fait un scuba parfait en sortant du métro",
           "a payé la fanum tax du goûter de toute la classe sans rien dire", "a mewé pendant toute la photo de classe",
           "a dit « skill issue » au GPS quand il s'est recalculé", "a répondu « Ohio » à la question « d'où venez-vous » à l'entretien d'embauche, et a décroché le poste"])
    c = p(["La salle a explosé.", "Personne n'a osé rire, on a juste applaudi.", "J'ai vu un homme naître.", "Le silence était sacré.",
           "Même le surveillant a validé."])
    return f"{a} {b}. {c} {p(['+2000 aura', '+1500 aura 🗿', 'W énorme', 'aura farming certifié', '+3000 aura, pas de débat'])}", p(
        ["Brainrot bien placé avec un timing comique parfait.", "Anecdote internet drôle et assurée.",
         "Référence maîtrisée, effet de groupe garanti."])

def br_correcte():
    return p([
        f"J'ai fait un scuba en sortant de la piscine, {p(['mes potes ont validé', 'le maître-nageur a souri', 'une mamie a applaudi'])}. +{R.choice([100, 200, 300])} aura",
        f"Pas de fanum tax sur mes {p(['frites', 'nuggets', 'chips', 'Pépito'])} aujourd'hui, j'ai faim. Demain peut-être.",
        f"Moi : je vais dormir tôt. Aussi moi à 3h : regarde des compilations de {p(['Tralalero Tralala', 'Tung Tung Tung Sahur', 'capybaras'])}.",
        f"Mon chat fait le mewing depuis sa naissance, c'est lui le vrai sigma de la maison 🐈",
        f"J'ai dit « six-sept » en réunion par réflexe. {p(['Personne a compris', 'Mon stagiaire a ri', 'Mon boss a dit sept-huit'])}, je reste fier.",
        f"Skill issue ? Non. Wi-Fi issue. {p(['Respectez-moi.', 'Nuance importante.', 'Je maintiens.'])}",
        f"Aura farming discret : j'ai rendu la monnaie exacte à la boulangerie {p(['sans chercher', 'du premier coup', 'en pièces de 10 centimes'])}.",
    ]), p(["Brainrot léger et autodérisoire, ça passe.", "Référence internet sympa sans en faire trop.", "Humour moderne correct, petit plus d'aura."])

def br_neutre():
    return p([
        "Le « 6-7 » est une tendance où on balance les mains en disant « six-sept ». Je sais pas d'où ça vient.",
        f"Mon petit frère dit « {p(['skibidi', 'sigma', 'Ohio', 'aura'])} » toutes les deux phrases, je sais pas trop ce que ça veut dire.",
        "Quelqu'un peut m'expliquer ce que veut dire « fanum tax » ? Merci.",
        f"Le mot « rizz » a été élu mot de l'année par {p(['un dictionnaire anglais', 'Oxford', 'un dictionnaire en ligne'])}.",
        "Le mewing consiste à placer la langue contre le palais pour, paraît-il, affiner la mâchoire.",
        f"Article du jour : « Les termes d'argot internet chez les {p(['12-15 ans', 'collégiens', 'lycéens'])} ». Lecture de 4 minutes.",
        "Vu une vidéo de Tralalero Tralala. C'est un requin avec des baskets. Ok.",
        f"Exposé de {p(['français', 'sociologie', 'SES'])} : le vocabulaire des réseaux sociaux. À rendre lundi.",
        "Le terme « sigma » vient d'une classification des personnalités popularisée en ligne.",
        "Ma fille m'a dit que j'avais « -100 aura » parce que j'ai mis des chaussettes avec des sandales. Je note.",
        "Tendance du mois : faire le « scuba » en vidéo. Je n'ai pas d'avis.",
        "Mon neveu m'a demandé si je connaissais l'Ohio. J'ai dit que c'était un État américain. Il a soupiré.",
        "Sondage en classe : 18 élèves sur 25 disent « six-sept » au moins une fois par jour.",
        "« Fanum tax » : le fait de prendre un peu de la nourriture d'un ami. Voilà, c'est noté.",
    ]), p(["Description factuelle du brainrot, aura nulle.", "Constat neutre sur la culture internet.", "Question informative sans style."])

def br_faible():
    a = p(["jsuis trop sigma", "regardez mon mewing", "jai trop d'aura", "jsuis le roi du rizz", "personne a mon aura"])
    b = p(["jai mewé pendant 3h ma mâchoire fait mal 😭", "mais personne me répond en dm", "jai fait le 6-7 au conseil de classe on m'a exclu 2 jours",
           "jai fait un scuba dans le couloir et jai glissé", "jai dit « gyatt » à ma prof par erreur je voulais dire « j'ai »",
           "mais ma mère m'appelle encore mon poussin"])
    c = p(["c normal ?", "-500 aura", "bon", "😔", "qqn me rassure", ""])
    return typo(f"{a} {b} {c}".strip()), p(["Brainrot forcé qui révèle l'inverse de l'aura visée.", "Try-hard internet qui finit en L.",
                                            "Revendication d'aura immédiatement démentie."])

def br_anti():
    return p([
        f"SKIBIDI GYATT OHIO RIZZ 6-7 6-7 6-7 FANUM TAX SIGMA SIGMA BOY 🗿🗿🗿 (j'ai {R.choice([34, 41, 47, 52])} ans)",
        f"Bonjour les jeunes ! Votre prof de techno est très « rizz » et « Ohio » aujourd'hui ! Qui veut faire un dab avec moi pour l'exposé ? 😎",
        f"jai fait payer la fanum tax a mon petit frère de 6 ans il pleure ma mère m'a privé de wifi {p(['mais jsuis sigma', 'skill issue de sa part', 'L énorme'])}",
        f"j'ai tatoué « AURA » sur mon front et j'ai écrit « ORA » {p(['🗿', '😭😭', 'le tatoueur a dit cé stylé'])}",
        f"mon crush ma ghost alors jlui ai envoyé 47 vocaux de moi qui fais le 6-7 {p(['elle a bloqué', 'sa mère a répondu', 'elle a déménagé'])}",
        f"Je fais du mewing en entretien d'embauche depuis 6 mois. Toujours au chômage. C'est les recruteurs qui sont pas sigma.",
        f"Wesh j'ai dit « {p(['gyatt', 'rizz', 'skibidi'])} » à l'enterrement de mon oncle pour détendre l'ambiance. Aura -10 000.",
        f"Mon CV : compétences — mewing (expert), 6-7 (bilingue), fanum tax (certifié). Je comprends pas pk on me rappelle pas.",
        f"Je me suis inscrit à un séminaire de « sigma mindset » à 1499€. On a fait des pompes en criant « Ohio ». Je recommande.",
    ]), p(["Brainrot hors contexte et désespéré : aura négative absolue.", "Usage gênant et pathétique des références internet.",
           "Cringe de niveau légendaire, mais à l'envers."])

# ============================================================ MODERNE (bios / messages / 3h du mat)
def mod_divine():
    return p([
        "Bio : Je ne swipe pas. Je laisse le destin faire défiler.",
        "3h12. Je ne t'écris pas parce que je pense à toi. Je t'écris parce que la ville dort et que tu es la seule chose qui ne m'ennuie pas.",
        "Insta : Pas de story. Pas de filtre. Quelques photos de ciels, et des gens qui se demandent où c'était.",
        "Tinder : Je n'ai pas de phrase d'accroche. J'ai une table réservée, un bon vin et une conversation qui te manquera.",
        "Vu à 3h. Répondu à 9h. Entre les deux, j'ai décidé que tu méritais une vraie réponse : oui.",
        "Bio : Né un mardi, comme les grandes décisions. 🗿",
        "Je ne fais pas de premier pas. Je fais le seul qui compte.",
        "Bio : J'ai lu tous les livres que tu prétends avoir lus. On en parle autour d'un verre ?",
        "2h58. Je ne dors pas, je supervise la nuit. Elle se tient bien ce soir, grâce à toi.",
        "Tinder : Je suis le plot twist de ton année. Swipe avec prudence.",
        "Story : un ticket de train pour nulle part, et la légende « reviens si tu peux ».",
        "Je ne réponds jamais aux « tu fais quoi ? ». Je réponds aux « viens ».",
    ]), p(["Message moderne d'une économie et d'un aplomb absolus.", "Rizz souverain en format réseau social.",
           "Mystère et assurance condensés en deux lignes."])

def mod_legend():
    a = p(["Bio :", "Tinder :", "Insta :", "3h04 —", "WhatsApp, 2h47 :"])
    b = p(["Je réponds lentement, mais je ne réponds jamais à moitié.", "Pas là pour plaire. Là pour choisir.",
           "Si tu cherches quelqu'un de simple, je suis simple. Juste rare.",
           "Je ne dors pas, je laisse la nuit m'écrire.", "Je t'ai pas oublié. Je t'ai rangé dans les choses précieuses, celles qu'on sort rarement.",
           "Ma mâchoire fait son mewing toute seule, moi je m'occupe du reste."])
    return f"{a} {b}", p(["Message moderne élégant et sûr de lui.", "Bio sélective qui donne envie d'écrire.", "Rizz posé avec une touche de mystère."])

def mod_forte():
    a = p(["Je ramène des croissants le dimanche et des vérités le lundi.", "Grande gueule, grand cœur, petite valise.",
           "Je fais les meilleures pâtes de l'arrondissement, demande à mes ex.", "Je te bats au Uno, au padel et aux débats sur les films."])
    b = p(["Viens vérifier.", "Swipe si t'assumes.", "Le premier verre est pour moi, le deuxième pour toi.", "Pas de « salut ça va », sois créatif."])
    return f"{a} {b}", p(["Bio assurée et drôle, rizz efficace.", "Confiance joueuse et défi lancé.", "Personnalité forte et accroche claire."])

def mod_correcte():
    return p([
        f"Ingé {p(['data', 'BTP', 'son', 'agro'])} le jour, cuisinier moyen le soir. Je cherche quelqu'un pour goûter mes ratés.",
        f"2h40 : tu dors ? Pas grave, je t'envoie juste ce {p(['mème de capybara', 'TikTok de chat', 'son de 2009'])}, tu me diras demain.",
        f"Fan de {p(['randos', 'musées', 'brocantes', 'concerts'])} et de cafés en terrasse même en novembre ☕",
        f"J'ai acheté deux places pour {p(['un concert', 'le ciné', 'une expo'])}. La deuxième attend quelqu'un de cool.",
        f"Petite bio honnête : je ris fort, je danse mal, je rends toujours les tupperwares.",
        "Je suis le pote qui a toujours un chargeur, un mouchoir et un mauvais jeu de mots.",
        "1h50 : j'ai trouvé une recette de crêpes à 3 ingrédients, je te réveille demain avec ça.",
        f"Bio : {p(['Prof de SVT', 'Kiné', 'Graphiste', 'Boulanger'])}, champion de karaoké de mon immeuble. Le titre n'est pas contesté.",
        "Mon plan pour ce soir : pizza, film d'horreur, et faire semblant de pas avoir peur. Tu viens ?",
        "Si tu aimes les chiens, les jeux de société et les gens qui arrivent à l'heure, on va s'entendre.",
        "3h : je viens de comprendre la fin d'Inception. Je t'appelle demain, c'est grave.",
    ]), p(["Message moderne sympathique et réussi.", "Bio honnête et chaleureuse.", "Ton léger, petite dose de charme."])

def mod_neutre():
    return p([
        f"{p(['Infirmière', 'Commercial', 'Étudiante en droit', 'Comptable'])}, {R.randint(23, 41)} ans, {p(['Nantes', 'Toulouse', 'Lille', 'Rennes'])}. J'aime le cinéma.",
        "3h : t'as pensé à éteindre le four ?",
        "Dispo samedi après-midi si tu veux, sinon dimanche.",
        f"Groupe WhatsApp « {p(['Famille', 'Coloc', 'Foot du jeudi'])} » : qui a pris le chargeur blanc ?",
        "Bien arrivé. Je t'appelle demain.",
        "Le colis est arrivé, je l'ai mis dans l'entrée.",
        f"Bio : {p(['Graphiste', 'Prof des écoles', 'Technicien', 'Pharmacienne'])}. Randonnée et séries.",
        "Rappel : réunion parents-profs jeudi 18h.",
        "Tu peux me renvoyer l'adresse ?",
        "Le Wi-Fi a encore sauté, je redémarre la box.",
        "1h30 : je rentre, le bus a eu du retard.",
        "Je suis à la caisse, tu veux autre chose ?",
    ]), p(["Message banal et fonctionnel.", "Bio informative sans relief.", "Logistique pure."])

def mod_faible():
    return typo(p([
        "tu dors ? moi non plus. enfin si mais non. bref jsp pk jécris",
        f"Bio : Je sais pas quoi mettre lol. {p(['J’aime manger', 'Mon pote m’a inscrit', 'Fan de séries'])}. Voilà.",
        "3h17 : jsuis pas bourré. 3h19 : un peu. 3h22 : tu me manques. 3h23 : oublie",
        f"Salut ! Désolé si je dérange, je voulais juste dire que {p(['ta story était cool', 't’as l’air sympa', 'je t’ai vu au ciné'])}… enfin voilà 😅",
        "J'ai rédigé ce message 14 fois. Celle-là c'est la moins pire. Coucou.",
        "Coucou ! Ça fait longtemps hein ? Bon ben… voilà… coucou quoi.",
        "Bio : Introverti mais sympa quand on me connaît (personne me connaît).",
        "2h : tu crois qu'on peut être ami avec son ex ? (pour un ami)",
        "Désolé pour hier soir. Et pour avant-hier. Et pour le message de ce matin. Bonne journée !",
        "Moi en story : photo du ciel, 2 vues, dont moi.",
        "Je t'ai envoyé un mème y'a 3 jours, tu l'as vu ? C'était drôle je crois.",
    ])), p(["Message hésitant et needy, aura en berne.", "Maladresse et sur-excuse.", "Bio sans effort ni personnalité."])

def mod_anti():
    return typo(p([
        "réponds. réponds. réponds. réponds. jvois que t'es en ligne. RÉPONDS",
        f"Bio : 1m{R.randint(66, 74)} (1m80 dans mon cœur). Pas de filles compliquées. Sigma uniquement. Mon ex est folle (elle dit pareil de moi).",
        "3h : jvais me présenter devant chez toi avec une enceinte et mettre notre son. 3h05 : ta mère a appelé la police",
        f"Je t'ai écrit un poème : roses are red, Ohio est {p(['bleu', 'loin', 'en Amérique'])}, réponds-moi ou je pleure 🥺🥺🥺",
        "J'ai fait une capture de ton « vu » et je l'ai mise en fond d'écran pour me motiver.",
        "Si tu me réponds pas d'ici 5 minutes je like toutes tes photos de 2017. Je suis sérieux.",
        "Bio : cherche une femme qui cuisine, qui nettoie et qui me laisse jouer à la Play. Pas de prise de tête 👑",
        "4h : jsuis devant ton immeuble mais jai oublié le code, tu peux descendre ? c'est une surprise",
        "J'ai créé un faux compte pour voir si tu m'avais bloqué. T'as bloqué le faux aussi. Comment t'as su ??",
        "Mon type de meuf : belle, riche, drôle, qui parle pas trop. Moi : là, sur mon canapé.",
    ])), p(["Insistance malaisante, aura négative absolue.", "Red flags en cascade.", "Désespoir numérique sans aucun filtre."])

# ============================================================ PROSE (minoritaire)
def prose_top():
    return p([
        "La ville s'est éteinte fenêtre après fenêtre, et je suis resté debout, à compter les lumières comme on compte ses victoires : sans bruit, et sans jamais finir.",
        "Je n'ai pas de royaume. J'ai une fenêtre sur la mer, un silence qui m'obéit, et la certitude tranquille que l'aube me doit des excuses.",
        "J'ai appris le calme auprès des cathédrales, et la patience auprès des fleuves. Le reste, je l'ai inventé.",
        "On ne me cherche pas. On me reconnaît, comme on reconnaît une chanson qu'on n'a jamais entendue.",
        "Les tempêtes ne crient pas : elles arrivent. Je fais pareil.",
        "Je ne suis pas entré dans la pièce : c'est la pièce qui s'est réorganisée autour de moi.",
        "J'ai traversé l'hiver sans manteau, et c'est l'hiver qui s'en souvient.",
        "Quand je me tais, les horloges hésitent.",
    ]), p(["Prose ciselée d'une souveraineté poétique.", "Images amples et voix dominante.", "Élégance lapidaire et mystère."])

def prose_mid():
    return p([
        "Pluie fine, café noir, et cette impression que la journée m'attendait.",
        "Je garde de chaque ville un ticket de métro, et de chaque personne une phrase.",
        "Le dimanche a des lenteurs qu'on devrait apprendre par cœur.",
        "J'ai rangé mes regrets dans un carton marqué « fragile ». Je ne l'ouvre plus, mais je le déménage toujours.",
        "La mer revient toujours, sans rancune. J'essaie d'apprendre.",
        "Il y a des gares où l'on n'attend aucun train, juste le courage de partir.",
        "Je collectionne les cartes postales que je n'envoie jamais ; elles finissent par me répondre.",
    ]), p(["Petite prose élégante et sensible.", "Image juste, ton maîtrisé.", "Joli sens du détail."])

def prose_low():
    return p([
        "La pluie tombe. Je suis triste. Le café est froid. La vie, voilà.",
        "Mon âme est un océan de ténèbres (sauf le mercredi, j'ai badminton).",
        "Le soleil se couche comme un gros jaune d'œuf sur la poêle du ciel.",
        "Je suis comme le vent : personne me voit et ça m'énerve.",
        "Tes yeux sont comme deux billes de couleur yeux.",
        "Mon cœur est un frigo vide : il fait du bruit la nuit et personne ne l'ouvre.",
        "Je suis une rose. Avec des épines. Et un peu de puceron.",
    ]), p(["Poésie plate ou métaphore ratée.", "Mélancolie de surface, images maladroites.", "Lyrisme involontairement comique."])

# ============================================================ PLAN PAR CLASSE
PLAN = {
    "Aura Divine":     [("politique", pol_divine, 34), ("brainrot", br_divine, 22), ("hybride", hyb, 12), ("moderne", mod_divine, 6), ("prose", prose_top, 5), ("politique", pol_legend, 0)],
    "Aura Légendaire": [("politique", pol_legend, 30), ("politique", pol_debat, 6), ("brainrot", br_legend, 26), ("hybride", hyb, 6), ("moderne", mod_legend, 22), ("prose", prose_top, 10)],
    "Forte Aura":      [("politique", pol_debat, 32), ("brainrot", br_forte, 34), ("moderne", mod_forte, 26), ("prose", prose_mid, 8)],
    "Aura Correcte":   [("politique", pol_terrain, 32), ("brainrot", br_correcte, 34), ("moderne", mod_correcte, 26), ("prose", prose_mid, 8)],
    "Aura Neutre":     [("politique", pol_neutre, 36), ("brainrot", br_neutre, 32), ("moderne", mod_neutre, 32)],
    "Aura Faible":     [("politique", pol_faible, 34), ("brainrot", br_faible, 34), ("moderne", mod_faible, 24), ("prose", prose_low, 8)],
    "Anti-Aura":       [("politique", pol_anti, 34), ("brainrot", br_anti, 36), ("moderne", mod_anti, 24), ("prose", prose_low, 6)],
}
# Divine a 79 « prévus » + complément
PLAN["Aura Divine"][-1] = ("politique", pol_legend, 0)

def components(cname, style):
    lo, hi = [(l, h) for n, l, h in CLASSES if n == cname][0]
    for _ in range(5000):
        target = R.uniform(lo, hi)
        comp = {k: max(-100, min(100, round(target + OFF[style][k] + R.gauss(0, 9)))) for k in W}
        sc = round(sum(comp[k] * W[k] for k in W))
        if cls_of(sc) == cname:
            return comp, sc
    raise RuntimeError(cname)

rows, seen = [], set()
for cname, _, _ in CLASSES:
    plan = PLAN[cname]
    quota = []
    for st, fn, n in plan: quota += [(st, fn)] * n
    # compléter à 100 avec les générateurs les plus riches
    rich = [(st, fn) for st, fn, n in plan if n >= 20]
    while len(quota) < 100: quota.append(p(rich))
    quota = quota[:100]
    allg = [(st, fn) for st, fn, n in plan if n > 0]
    done, tries = 0, 0
    while done < 100 and tries < 200000:
        tries += 1
        st, fn = quota[done] if R.random() < 0.6 else p([g for g in allg if g[0] != 'politique'] if R.random() < 0.7 else allg)
        text, just = fn()
        if text in seen:
            continue
        seen.add(text)
        comp, sc = components(cname, st)
        rows.append(dict(texte=text, classe=cname, score=sc, justification=just, style=st, **comp))
        done += 1
    print(cname, done, tries)

R.shuffle(rows)
cols = ["texte", "classe", "score", "justification", "style", "R", "S", "O", "B", "M", "P"]
with open("aura_dataset_v2.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

# bilan
print(len(rows), len(seen))
ct = defaultdict(Counter)
for r in rows: ct[r["classe"]][r["style"]] += 1
for cname, _, _ in CLASSES:
    sc = [r["score"] for r in rows if r["classe"] == cname]
    print(cname, sum(ct[cname].values()), dict(ct[cname]), "score moy", round(sum(sc) / len(sc), 1), min(sc), max(sc))
print(Counter(r["style"] for r in rows))
