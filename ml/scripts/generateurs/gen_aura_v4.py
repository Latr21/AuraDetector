"""Aura v4 : gros lot synthétique, registres variés, ~700 textes par classe.
Formule sans Mystère : 0.333R + 0.222S + 0.167O + 0.167B + 0.111P."""
import random, csv, itertools, re
def sk(t): return re.sub(r'\d+', '#', t.lower().strip())
from collections import Counter, defaultdict

R = random.Random(404)
p = R.choice
def S(x, k): return R.sample(x, k)

CLASSES = [("Anti-Aura", -100, -41), ("Aura Faible", -40, -11), ("Aura Neutre", -10, 4), ("Aura Correcte", 5, 24),
           ("Forte Aura", 25, 49), ("Aura Légendaire", 50, 74), ("Aura Divine", 75, 100)]
W = dict(R=0.30 / .9, S=0.20 / .9, O=0.15 / .9, B=0.15 / .9, P=0.10 / .9)
OFF = {"argot": dict(R=5, S=0, O=18, B=-8, P=-12), "politique": dict(R=5, S=15, O=-10, B=5, P=-5),
       "moderne": dict(R=10, S=-3, O=0, B=-5, P=-12), "prose": dict(R=-10, S=-8, O=-5, B=18, P=18),
       "hybride": dict(R=0, S=0, O=15, B=5, P=10), "classique": dict(R=-5, S=5, O=-5, B=15, P=20),
       "quotidien": dict(R=-3, S=0, O=-8, B=-3, P=-10), "juridique": dict(R=-10, S=5, O=-15, B=0, P=-10)}
def cls_of(s): return next((n for n, lo, hi in CLASSES if lo <= s <= hi), None)

def typo(t, prob=0.5):
    for a, b in [("c'est", "cé"), ("je suis", "jsuis"), ("pourquoi", "pk"), ("vraiment", "vrmt"), ("quoi", "koi"),
                 ("je sais pas", "jsp"), ("tout le monde", "tlm"), ("quand même", "qd mm"), ("toujours", "tjr"),
                 ("beaucoup", "bcp"), ("aujourd'hui", "ajd"), ("d'accord", "dac"), ("s'il te plaît", "stp")]:
        if a in t and R.random() < prob: t = t.replace(a, b)
    return t

NOMS = ["Leroux", "Marchand", "Benali", "Fontaine", "Garnier", "Lemoine", "Moreau", "Perrin", "Caron", "Delmas",
        "Roussel", "Nguyen", "Vasseur", "Morel", "Barbier", "Hamidi", "Chevalier", "Lacroix", "Mercier", "Royer",
        "Brunet", "Collin", "Da Silva", "Faure", "Guérin", "Joly", "Kessler", "Laurent", "Meyer", "Pons"]
CIV = ["M.", "Mme"]
MIN = ["ministre de l'intérieur", "ministre de la santé", "ministre du travail", "ministre de l'éducation nationale",
       "ministre de l'agriculture", "ministre des comptes publics", "ministre des armées", "ministre de la culture",
       "ministre de la transition écologique", "ministre des transports", "ministre du logement",
       "ministre délégué chargé du numérique", "ministre de la justice"]
SUJ = ["les urgences", "la retraite des agriculteurs", "les classes surchargées", "le prix de l'électricité",
       "les déserts médicaux", "la sécurité dans les transports", "le logement étudiant", "les petites lignes ferroviaires",
       "la dette publique", "les collectivités locales", "les PME", "les apprentis", "la police de proximité",
       "les maternités qui ferment", "le pouvoir d'achat", "la filière nucléaire", "les AESH", "les feux de forêt",
       "l'eau potable", "la fraude sociale", "la fraude fiscale", "le harcèlement scolaire", "la ruralité", "les outre-mer"]
PUBLIC = ["agriculteurs", "retraités", "soignants", "enseignants", "commerçants", "maires", "étudiants", "artisans",
          "policiers", "chauffeurs routiers", "aides-soignantes", "pompiers", "infirmières", "jeunes"]
VILLES = ["Rodez", "Vierzon", "Lens", "Montluçon", "Saint-Brieuc", "Dax", "Épinal", "Châteauroux", "Mulhouse", "Tarbes",
          "Cherbourg", "Albi", "Bourges", "Laval", "Valence", "Besançon", "Aurillac", "Lorient", "Nevers", "Arras"]

# ====================================================================== HÉMICYCLE
def hem_neutre():
    return p([
        p(["Très bien !", "Exactement !", "C'est vrai !", "Bravo !", "Absolument !", "Tout à fait !", "Et alors ?",
           "Excellent !", "Bien sûr !", "Évidemment !", "Ah !", "C'est juste !", "Voilà !", "Merci !", "Oui !"]),
        f"Et les {p(PUBLIC)} ?", f"Et {p(SUJ)} ?", f"Et pour {p(SUJ)} ?",
        f"Et les {p(PUBLIC)}, alors ?", f"Et à {p(VILLES)} ?",
        f"Vous gouvernez depuis {R.randint(2, 12)} ans !", f"C'était il y a {R.randint(2, 9)} ans !",
        f"Rappel au règlement !", f"Article {R.randint(40, 100)} !",
    ]) + p(["", "", "", " (Applaudissements sur plusieurs bancs.)", " (Exclamations.)", " (Murmures.)"]), \
        p(["Interjection d'hémicycle banale, sans relief.", "Réaction réflexe de séance, aura neutre.",
           "Approbation ou objection sans trouvaille."])

def hem_faible():
    return p([
        p(["Menteur !", "Honteux !", "Scandaleux !", "Démission !", "C'est n'importe quoi !", "Rendez l'argent !",
           "Vous êtes nuls !", "Dehors !", "Arrêtez de mentir !", "C'est lamentable !", "Mais taisez-vous !",
           "Pitoyable !", "Quelle honte !", "C'est faux, archi-faux !", "Ridicule !", "N'importe quoi !",
           "Ça suffit !", "Incompétents !", "Allez, rentrez chez vous !", "Mensonge !"]),
        f"{p(['Menteur', 'Honteux', 'Scandaleux', 'Lamentable'])} ! {p(['Menteur', 'Honteux', 'Scandaleux', 'Lamentable'])} !",
        f"C'est {p(['du pipeau', 'du vent', 'du blabla', 'de la com', 'du théâtre'])} !",
        f"Vous {p(['mentez', 'trichez', 'bricolez', 'improvisez'])} depuis le début !",
    ]) + p(["", "", " (Vives protestations.)", " (Brouhaha.)", " (Mme la présidente rappelle l'orateur à l'ordre.)"]), \
        p(["Cri sec sans trouvaille : le statut baisse.", "Insulte d'hémicycle qui sonne comme un aveu de faiblesse.",
           "Agressivité brute, aucune finesse."])

def hem_correcte():
    return p([
        f"Il a découvert {p(['la lune', 'l’eau tiède', 'le fil à couper le beurre', 'la poudre', 'l’Amérique'])} !",
        f"Encore un {p(['rapport', 'comité', 'Grenelle', 'numéro vert', 'plan', 'observatoire'])}, ça va tout changer !",
        f"Bel effort de {p(['mémoire', 'lecture', 'cohérence', 'créativité'])} !",
        "Vous lisez vos fiches ou vous pensez ?", "On a connu des réformes plus courageuses !",
        f"Le {p(['ministre', 'rapporteur', 'gouvernement'])} découvre le dossier en direct !",
        f"C'est {p(['l’hôpital', 'la charité', 'le pompier pyromane'])} qui se moque de {p(['la charité', 'l’hôpital', 'l’incendie'])} !",
        f"Vous avez la mémoire courte et la facture longue !", "Pour la sincérité, on repassera !",
        f"Vous parlez de {p(SUJ)}, les {p(PUBLIC)} en rient encore !", "Quel aveu !", "Lapsus révélateur !",
        "Ça, c'est un programme !", "Vous confondez vitesse et précipitation !",
    ]), p(["Pique ironique bien placée, petite aura.", "Interjection spirituelle qui fait mouche.",
           "Ironie de séance efficace mais modeste."])

def hem_proc():
    n = f"{p(CIV)} {p(NOMS)}"
    return p([
        f"La parole est à {n}.", f"La parole est à {n}, pour le groupe {p(['majoritaire', 'd’opposition', 'non inscrit'])}.",
        f"La parole est à {p(['M. le', 'Mme la'])} {p(MIN)}.", "La séance est suspendue.",
        f"La séance est suspendue. Elle est reprise à {R.randint(14, 23)} heures {p(['', 'quinze', 'trente', 'cinquante'])}.".replace("  ", " ").replace(" .", "."),
        f"Je mets aux voix l'amendement n° {R.randint(1, 3500)}.", "(L'amendement n'est pas adopté.)", "(L'amendement est adopté.)",
        f"Sur l'article {R.randint(1, 60)}, je suis saisie de {R.randint(2, 90)} amendements.",
        "Le scrutin est ouvert.", "Le scrutin est clos.", f"Voici le résultat du scrutin : {R.randint(300, 577)} votants.",
        f"Quel est l'avis de la commission ?", "Avis défavorable.", "Avis favorable.", "Sagesse.",
        f"{n}, votre temps de parole est écoulé.", "Mes chers collègues, un peu de silence, s'il vous plaît.",
        f"Prochaine séance, {p(['demain', 'mardi', 'mercredi', 'jeudi'])}, à {p(['9', '15', '21'])} heures.",
        f"L'ordre du jour appelle la suite de la discussion du projet de loi relatif {p(['à la simplification', 'au logement', 'à la santé au travail', 'à l’énergie', 'à la sécurité intérieure'])}.",
    ]), p(["Ligne de procédure parlementaire, strictement neutre.", "Formule de présidence sans charge.",
           "Langage procédural, aura nulle."])

def qag(tier):
    n = f"{p(['Monsieur', 'Madame'])} {p(['le', 'la'])} {p(MIN)}" if R.random() < .7 else f"{p(['Monsieur', 'Madame'])} {p(['le premier ministre', 'la première ministre'])}"
    n = n.replace("Monsieur la", "Madame la").replace("Madame le", "Madame la") if "première" in n or "Madame" in n else n
    suj = p(SUJ); pub = p(PUBLIC); v = p(VILLES)
    if tier == "neutre":
        t = f"{n}, ma question porte sur {suj}. {p(['Quel calendrier envisagez-vous ?', 'Quelles mesures comptez-vous prendre ?', 'Pouvez-vous nous indiquer les moyens prévus ?', 'Où en est le décret d’application ?'])}"
        j = "Question au gouvernement factuelle, sans relief."
    elif tier == "faible":
        t = (f"{n}, alors voilà, je voulais vous interroger, enfin vous poser une question, sur {suj}, parce que, comme vous le savez, "
             f"ou peut-être ne le savez-vous pas, {p(['c’est un sujet important', 'c’est compliqué', 'les gens m’en parlent', 'il y a des choses à dire'])}. "
             f"{p(['Donc ma question est : qu’en pensez-vous ?', 'Voilà. Je vous remercie.', 'Euh, je reprends ma fiche.', 'Bref, que comptez-vous faire, en gros ?'])}")
        j = "Question confuse et hésitante, l'orateur perd la salle."
    elif tier == "correcte":
        t = (f"{n}, à {v}, les {pub} attendent depuis {R.randint(2, 11)} ans. {p(['Ils ne demandent pas des promesses, ils demandent une date.', 'Ils ont vu passer trois plans et aucun résultat.', 'Ils connaissent vos annonces par cœur ; ils attendent les actes.'])} "
             f"{p(['Quand ?', 'Allez-vous enfin agir ?', 'Quelle est votre réponse ?'])}")
        j = "Question concrète et bien tournée, aura correcte."
    else:  # forte
        t = (f"{n}, {p(['vous aviez promis', 'vous aviez juré', 'vous aviez annoncé'])} {p(['la rupture', 'la simplification', 'le choc', 'la révolution'])}. "
             f"{p(['Nous avons eu la continuité.', 'Nous avons eu un rapport.', 'Nous avons eu une conférence de presse.'])} "
             f"À {v}, les {pub} {p(['ne lisent pas vos communiqués : ils lisent leurs factures.', 'n’ont plus le temps d’attendre votre méthode.', 'ont compris avant vous.'])} "
             f"{p(['Alors je vous le demande, les yeux dans les yeux : quand ?', 'Qu’allez-vous leur dire, ce soir ?', 'Assumez-vous ce bilan ?'])}")
        j = "Question incisive : contraste, rythme et chute dominante."
    return t, j

def rep_ministre(tier):
    n = f"{p(['Monsieur', 'Madame'])} {p(['le député', 'la députée'])}".replace("Monsieur la", "Madame la").replace("Madame le", "Monsieur le")
    suj = p(SUJ)
    if tier == "faible":
        t = (f"{n}, merci de m'interroger sur ce dossier, ce qui me donne l'occasion de redire la mobilisation pleine et entière de l'État concernant {suj}. "
             f"{p(['Nous avons engagé une démarche globale, transversale et partenariale.', 'Un travail est en cours, il se poursuit et il se poursuivra.', 'Une concertation sera lancée pour préparer la concertation.', 'Les choses avancent, et elles avanceront encore, dans le cadre d’une méthode.'])} "
             f"{p(['Soyez assuré de notre pleine mobilisation.', 'Nous y reviendrons.', 'Le gouvernement est à vos côtés.'])}")
        j = "Langue de bois ministérielle : beaucoup de mots, aucune présence."
    elif tier == "neutre":
        t = f"{n}, s'agissant de {suj}, {R.randint(2, 900)} millions d'euros ont été {p(['engagés', 'délégués', 'inscrits au budget'])} en {p(['2025', '2026'])}. {p(['Un décret paraîtra au premier trimestre.', 'Une évaluation est prévue à l’automne.', 'Les préfets ont reçu une instruction.'])}"
        j = "Réponse ministérielle factuelle, chiffrée, sans aura."
    elif tier == "correcte":
        t = f"{n}, je ne vais pas vous répondre par des slogans. Sur {suj}, voici ce qui est fait : {p(['des postes ouverts', 'des crédits débloqués', 'un calendrier publié'])}, et ce qui reste à faire : {p(['tout le reste', 'beaucoup', 'l’essentiel'])}. Je reviendrai devant vous avec des résultats."
        j = "Réponse honnête et structurée, aura correcte."
    else:
        t = (f"{n}, vous avez le droit de critiquer ; vous n'avez pas le droit d'oublier. "
             f"{p(['Ce que vous dénoncez aujourd’hui, vous l’avez voté hier.', 'Les chiffres que vous citez, c’est votre bilan, pas le nôtre.', 'Pendant que vous commentiez, nous agissions.'])} "
             f"{p(['Moi, je préfère les résultats aux indignations.', 'Les Français jugeront sur pièces.', 'Et je vous donne rendez-vous dans six mois.'])}")
        j = "Riposte ministérielle cinglante, dominance maîtrisée."
    return t, j

def tribune(tier):
    ana = p([("Voilà votre bilan", ["le chaos", "l'immobilisme", "la confusion", "le désordre", "l'impuissance"]),
             ("Debout", ["pour l'école", "pour nos villages", "pour l'hôpital", "pour ceux qui se lèvent tôt"]),
             ("Nous ne lâcherons rien", ["sur les salaires", "sur l'école", "sur la sécurité", "sur l'hôpital", "sur la ruralité"])])
    if tier == "forte":
        if ana[0] == "Voilà votre bilan":
            t = " ".join(f"{x.capitalize()} : voilà votre bilan !" for x in S(ana[1], 3))
        elif ana[0] == "Debout":
            t = "Alors levons-nous ! " + " ".join(f"Debout {x} !" for x in S(ana[1], 3))
        else:
            t = " ".join(f"Nous ne lâcherons rien {x} !" for x in S(ana[1], 3))
        j = "Anaphore de tribune efficace, rythme marqué."
    elif tier == "legend":
        t = p([
            f"On ne gouverne pas un pays comme on gère {p(['un tableur', 'une start-up', 'un sondage', 'une communication de crise'])}. Un pays, ça se regarde dans les yeux, ça s'écoute, et parfois ça se contredit. Ce soir, je vous demande de regarder la France en face.",
            f"Il y a ceux qui commentent l'histoire et ceux qui la font. Les premiers ont toujours raison le lendemain ; les seconds ont eu le courage la veille. Je vous propose d'être de ceux de la veille.",
            f"Vous parlez de {p(SUJ)} avec des chiffres ; moi, j'en parle avec des visages. Et ces visages, à {p(VILLES)} comme ailleurs, ne demandent pas qu'on les plaigne : ils demandent qu'on les respecte.",
            f"Le courage politique n'est pas de plaire à tout le monde ; c'est de déplaire pour de bonnes raisons. J'assume de déplaire.",
            f"La République n'est pas un décor qu'on sort pour les commémorations. C'est une promesse faite à {p(['chaque enfant', 'chaque citoyen', 'chaque village'])}, et une promesse, ça se tient.",
        ])
        j = "Période oratoire ample et maîtrisée, grande autorité."
    else:  # anti
        t = p([
            f"Mes chers compatriotes, j'annonce la création d'un {p(['haut-commissariat', 'comité Théodule', 'ministère'])} de {p(['l’aura', 'la bonne humeur', 'la vibe', 'la gagne'])}. Je le présiderai moi-même. Il n'y aura pas de budget.",
            f"Je suis le candidat du peuple ! Le peuple m'adore ! J'ai fait {R.randint(3, 40)} voix à {p(VILLES)}, c'est un raz-de-marée !",
            f"Rejoignez-moi ce soir pour le grand meeting de la renaissance ! (Salle des fêtes de {p(VILLES)}, {R.randint(3, 12)} participants dont ma mère.)",
            f"J'ai une vision pour la France. Je l'ai oubliée dans le taxi, mais elle était très belle.",
            f"Je n'ai jamais dit ce que j'ai dit. Et si je l'ai dit, c'était sorti de son contexte. Et le contexte, c'était moi.",
        ])
        j = "Grandiloquence ridicule et pathétique, aura détruite."
    return t, j

# ====================================================================== CLASSIQUE (pastiches originaux, aucun vers réel)
MAX_TOP = [
    "On pardonne aisément aux autres les fautes dont on est sûr de ne jamais rougir.",
    "La patience est une colère qui a appris à attendre son heure.",
    "Le silence d'un sage pèse plus lourd que l'éloquence de dix courtisans.",
    "Qui craint d'être oublié finit toujours par se faire remarquer pour de mauvaises raisons.",
    "Nous louons volontiers les morts ; ils ne nous font plus d'ombre.",
    "La gloire est un manteau qu'on admire de loin et qui pèse à qui le porte.",
    "Il n'est point de grandeur sans un peu de solitude, ni de solitude sans un peu d'orgueil.",
    "L'ambitieux grimpe ; le grand homme se contente de demeurer debout.",
    "On se lasse de tout, sauf d'avoir raison.",
    "La flatterie est une monnaie qui n'enrichit que celui qui la reçoit, et pour un temps seulement.",
    "Le courage véritable ne se montre pas ; il se devine à ce que l'on ne fait pas.",
    "Les promesses des puissants sont comme les nuages d'été : elles ombragent et ne mouillent point.",
    "Il faut beaucoup d'esprit pour se taire à propos.",
    "Le temps n'efface rien ; il range.",
    "Celui qui ne doute jamais n'a pas encore commencé à penser.",
    "L'orgueil des petits se voit ; celui des grands se cache sous la politesse.",
    "Nous jugeons les autres sur leurs actes, et nous-mêmes sur nos intentions.",
    "Une belle mort ne rachète pas une vie médiocre, mais elle la fait oublier.",
]
TIRADE_TOP = [
    "Je n'ai jamais plié devant la destinée,\nEt ma route est tracée avant que d'être née.",
    "Le trône n'est pour moi qu'un siège un peu plus haut :\nJe le quitte sans peine et j'y reviens s'il faut.",
    "Qu'on m'ôte la couronne, on ne m'ôtera pas\nCe calme souverain qui marche avec mes pas.",
    "Ma gloire n'attend pas qu'un roi la reconnaisse ;\nElle brille déjà sans qu'aucun vent l'abaisse.",
    "Ne me demandez pas d'oublier mon offense :\nJe pardonne aux vivants, je laisse au ciel l'enfance.",
    "J'ai vu les grands tomber, les flatteurs se taire,\nEt le temps se courber devant ma seule terre.",
    "Le sort m'a tout repris, sauf ce qui fait un homme :\nUn nom que l'on murmure et qu'à peine on renomme.",
    "Seigneur, ne craignez rien : mon cœur sait se contraindre,\nMais l'honneur qu'on offense est un feu dur à éteindre.",
]
VERS_RATES = [
    "Ô toi ma belle, ô toi ma rose,\nTu es jolie comme une chose.",
    "Ton œil est bleu comme le ciel,\nEt ta bouche est douce comme le miel,\nEt ton nez, ma foi, est un nez.",
    "Madame, votre beauté m'éblouit tellement fort\nQue j'en ai mal aux yeux et un peu aux dents aussi.",
    "Je t'aime comme un fou, je t'aime comme un poisson,\nQui nage dans l'eau, et voilà la chanson.",
    "Votre esprit est si fin qu'on ne le voit plus guère,\nC'est un compliment, enfin, c'est ce que j'espère.",
    "Ô lune, ô lune, toi qui es ronde,\nTu es la plus ronde du monde.",
]
FABLES = [  # (animal1, animal2, morale_qualité)
    ("Le Pigeon", "le Paon", "La vanité fait plus de bruit que de chemin."),
    ("La Taupe", "l'Aigle", "Qui ne voit rien juge de tout."),
    ("Le Chat", "le Grillon", "On méprise le chant tant qu'on n'a pas froid."),
    ("Le Renard", "la Pie", "Le bavard prête toujours sa langue à plus rusé que lui."),
    ("Le Hérisson", "le Lièvre", "La prudence arrive tard, mais elle arrive entière."),
    ("La Fourmi", "le Moustique", "Le plus petit des maux trouble le plus grand repos."),
    ("Le Bœuf", "le Chien", "Le fort n'a pas besoin d'aboyer."),
    ("Le Loup", "le Berger", "Qui garde le troupeau ne dort jamais tout à fait."),
    ("Le Corbeau", "le Hibou", "La sagesse se tait quand la sottise chante."),
    ("Le Lion", "le Moucheron", "Les plus grands périls naissent des plus petits mépris."),
]
def fable(tier):
    a, b, m = p(FABLES)
    if tier == "correcte":
        t = f"{a} et {b.capitalize()}\n\n{a} se croyait plus fin que {b} ;\nIl en fit la remarque, et s'en mordit les doigts.\nMoralité : {m}"
        j = "Fable pastiche honnête, morale juste mais vers simples."
    else:
        t = f"{a}, voyant passer {b},\nVoulut lui disputer l'empire de la route.\nIl parla, s'agita, puis demeura sans voix :\n{m}"
        j = "Fable rythmée avec une morale bien frappée."
    return t, j

# ====================================================================== JURIDIQUE / QUOTIDIEN
def juridique():
    org = p(["Le conseil départemental", "L'autorité administrative", "Le représentant de l'État", "La commission compétente",
             "L'employeur", "Le bailleur", "L'organisme gestionnaire", "Le maire", "Le chef d'établissement"])
    act = p(["peut, par décision motivée,", "est tenu de", "veille à", "peut", "doit, dans un délai de deux mois,"])
    obj = p(["informer les intéressés de la décision prise", "transmettre le dossier au service instructeur",
             "assurer la publicité des actes", "procéder à la notification par tout moyen", "fixer les modalités d'application",
             "communiquer les pièces justificatives", "réunir la commission au moins une fois par an"])
    t = f"Article {R.randint(1, 98)}{p(['', '-1', '-2', ' bis'])} — {org} {act} {obj}."
    if R.random() < .4: t += f" {p(['Un décret en Conseil d’État précise les conditions d’application du présent article.', 'Les dispositions du présent article entrent en vigueur le premier jour du mois suivant leur publication.', 'Le silence gardé pendant deux mois vaut rejet.'])}"
    return t, p(["Texte juridique impersonnel, aura nulle.", "Langage normatif sans charge émotionnelle.", "Disposition réglementaire neutre."])

def quotidien_neutre():
    return p([
        f"Le {p(['magasin', 'cabinet', 'bureau de poste', 'garage', 'pressing'])} sera fermé {p(['lundi', 'samedi', 'du 3 au 10', 'pendant les vacances'])}.",
        f"Pensez à {p(['sortir les poubelles', 'ramener les clés', 'payer la cantine', 'signer le carnet', 'arroser les plantes'])} {p(['ce soir', 'demain', 'avant vendredi'])}.",
        f"Réunion de copropriété le {R.randint(1, 28)} {p(['mars', 'avril', 'mai', 'juin', 'octobre'])} à {R.randint(17, 20)}h, salle commune.",
        f"Colis déposé en point relais, à retirer sous {R.randint(5, 14)} jours.",
        f"Votre rendez-vous du {R.randint(1, 28)}/{R.randint(1, 12):02d} est confirmé.",
        f"Coupure d'eau prévue {p(['mardi', 'jeudi'])} de {R.randint(8, 10)}h à {R.randint(12, 16)}h.",
        f"Le {p(['bus', 'tram', 'RER'])} {p(['C', '12', '4', 'B', '71'])} est {p(['dévié', 'interrompu', 'retardé'])} {p(['jusqu’à 20h', 'ce week-end', 'pour travaux'])}.",
        f"Ok, je {p(['passe', 't’appelle', 'te rejoins', 'regarde ça'])} {p(['après le boulot', 'dans 10 min', 'demain matin', 'ce soir'])}.",
        f"Tu as {p(['le code wifi', 'le numéro du plombier', 'les horaires de la piscine', 'le lien de la visio'])} ?",
        f"{p(['Bonne', 'Excellente'])} {p(['journée', 'soirée', 'semaine'])} à tous.",
        f"Ingrédients : {', '.join(S(['farine', 'beurre', 'sucre', 'œufs', 'lait', 'sel', 'levure', 'chocolat'], 4))}.",
        f"Température prévue demain : {R.randint(-2, 31)} °C.",
    ]), p(["Message pratique du quotidien, sans relief.", "Information banale et fonctionnelle.", "Communication neutre."])

def avis(tier):
    obj = p(["Restaurant", "Hôtel", "Aspirateur", "Casque audio", "Cours de yoga", "Coiffeur", "Livre", "Garage", "Box internet", "Pizzeria"])
    if tier == "neutre":
        t = f"{obj} : {p(['correct', 'conforme', 'dans la moyenne', 'sans surprise'])}. {p(['Rien à signaler.', 'Prix raisonnable.', 'Livraison dans les délais.', 'Accueil poli.'])} {R.randint(3, 4)}/5"
        j = "Avis client neutre et factuel."
    elif tier == "faible":
        t = typo(f"{obj} : bof bof. {p(['jai attendu 1h', 'le serveur ma regardé bizarre', 'ça marche mais jsp', 'cé pas ouf'])}. {p(['jmet 2 quand même', 'je sais pas trop', 'bref', 'voilà'])} {R.randint(1, 2)}/5")
        j = "Avis brouillon et mou, sans argument."
    else:
        t = f"{obj} : {p(['une claque.', 'une révélation.', 'un sans-faute.'])} {p(['Le genre d’endroit qu’on garde pour soi, mais je suis généreux.', 'J’y retourne demain, et après-demain par sécurité.', 'Mon ancien moi n’aurait pas cru ça possible.'])} 5/5"
        j = "Avis enthousiaste et bien tourné."
    return t, j

# ====================================================================== MODERNE (grosses combinatoires)
METIERS = ["Infirmière", "Dev", "Prof d'histoire", "Boulanger", "Juriste", "Kiné", "Graphiste", "Pompier", "Comptable",
           "Barista", "Ingé son", "Architecte", "Vétérinaire", "Doctorante", "Électricien", "Libraire", "Pilote", "Chef de projet"]
PASSIONS = ["la rando", "les brocantes", "le padel", "les films d'horreur", "la cuisine thaï", "les échecs", "les concerts",
            "la photo argentique", "les mangas", "le jardinage", "l'escalade", "les jeux de société", "la danse", "le vélo"]
def bio(tier):
    m, a, b = p(METIERS), p(PASSIONS), p(PASSIONS)
    if tier == "anti":
        t = typo(f"{p(['Pas de prise de tête', 'Que du sérieux', 'Sigma only'])}. {p(['Si t’as plus de 25 ans swipe left', 'Pas de meuf qui sort trop', 'Je veux une femme soumise mais drôle', 'Tu payes le premier verre, égalité oblige'])}. {p(['1m70 (1m85 en esprit)', 'Mon ex est folle', 'Je réponds pas aux pavés', 'Snap : roi_du_rizz_77'])} {p(['👑', '🐺', '💯', '😏'])}")
        j = "Bio repoussoir : exigences agressives et ego fragile."
    elif tier == "faible":
        t = f"{m}. {p(['Je sais pas quoi mettre', 'Mon pote m’a inscrit', 'Je suis nul pour les bios', 'Pas doué pour ça'])}. J'aime {a} je crois. {p(['Voilà', 'Bref', 'Écris-moi si tu veux, ou pas', '🤷'])}."
        j = "Bio sans effort ni conviction."
    elif tier == "neutre":
        t = f"{m}, {R.randint(22, 45)} ans. {a.capitalize()} et {b}. {p(['Plutôt calme.', 'Recherche une relation sérieuse.', 'Non fumeur.', ''])}".strip()
        j = "Bio descriptive sans relief."
    elif tier == "correcte":
        t = f"{m} le jour, {p(['fan', 'adepte', 'grande consommatrice', 'champion autoproclamé'])} de {a} le soir. {p(['Je te bats à', 'Je t’initie à', 'On teste ensemble'])} {b} {p(['si tu oses', 'au premier date', 'sans pitié'])}."
        j = "Bio vivante et personnelle, aura correcte."
    elif tier == "forte":
        t = f"{m}. {p(['Je parle peu, je fais beaucoup.', 'Je réponds lentement, mais jamais à moitié.', 'Je connais les bons bars et les mauvaises excuses.'])} {p(['Si tu aimes', 'Viens si tu aimes', 'Écris si tu aimes'])} {a} {p(['et les conversations qui finissent à 2h', 'et les gens qui tiennent parole', 'et les plans improvisés'])}."
        j = "Bio assurée et sélective, rizz réel."
    else:
        t = f"{m}. {p(['Je ne swipe pas, je choisis.', 'Pas là pour plaire. Là pour rencontrer.', 'Une table réservée, un bon vin, et une conversation qui te manquera.', 'Je laisse des portes entrouvertes et des souvenirs qui posent des questions.'])}"
        j = "Bio d'une économie parfaite, mystère et assurance."
    return t, j

HEURES = [f"{h}h{m:02d}" for h in (1, 2, 3, 4) for m in (2, 7, 13, 21, 34, 46, 58)]
def nuit(tier):
    h = p(HEURES)
    if tier == "anti":
        t = typo(f"{h} : {p(['réponds', 'jsais que tu lis', 'pk tu me ghost', 'je suis devant chez toi'])}. {h[:-2]}{int(h[-2:]) + 1:02d} : {p(['réponds stp', 'RÉPONDS', 'ok je pleure', 'ta mère a ouvert la fenêtre'])}. {p(['🥺🥺🥺', '😭😭', '...', 'je vais pas dormir'])}")
        j = "Harcèlement nocturne désespéré, aura en abîme."
    elif tier == "faible":
        t = typo(f"{h} : {p(['tu dors ?', 'je pense trop', 'j’arrive pas à dormir', 'ça va toi ?'])} {p(['enfin non oublie', 'c’est bête', 'désolé de te déranger', 'jsp pk j’écris'])} {p(['😅', '', '🙃'])}").strip()
        j = "Message nocturne hésitant et needy."
    elif tier == "correcte":
        t = f"{h} : je viens de {p(['finir la série', 'comprendre la fin du film', 'trouver une recette de crêpes à 3 ingrédients', 'voir un renard dans la rue'])}. {p(['On en parle demain, c’est grave.', 'Je te raconte au petit-déj.', 'Bonne nuit quand même.'])}"
        j = "Message nocturne léger et sympathique."
    elif tier == "forte":
        t = f"{h}. {p(['Je ne t’écris pas pour que tu répondes.', 'La ville dort, moi non.', 'Je ne dors pas, je réfléchis à ta question d’hier.'])} {p(['Juste pour que tu saches que tu as gagné le débat.', 'Demain, café. Je paie, tu parles.', 'La réponse est oui, mais je te le dirai en face.'])}"
        j = "Message de nuit assuré et intrigant."
    else:
        t = f"{h}. {p(['La lune a pris ta place à la fenêtre ; elle fait moins de bruit, mais elle brille moins.', 'Je ne dors pas, je supervise la nuit. Elle se tient bien, grâce à toi.', 'Les étoiles font leur travail. Moi, je pense au mien : te convaincre de venir.'])}"
        j = "Message nocturne poétique et souverain."
    return t, j

# ====================================================================== argot internet (grosses combinatoires)
SUJETS_BR = ["Le nouveau", "Mon pote Yanis", "La prof d'anglais", "Le chauffeur du 38", "Mon grand-père", "Le vigile du Lidl",
             "Ma cousine", "Le surveillant", "Le boulanger", "Mon coloc", "La CPE", "Le livreur Uber Eats", "Mon petit frère"]
ACTES_TOP = ["a fait le 6-7 pile quand la prof a dit « page 67 »", "a payé la fanum tax de toute la tablée sans un mot",
             "a mewé pendant toute la photo de classe", "a fait un scuba parfait en sortant du métro",
             "a répondu « skill issue » au GPS quand il s'est recalculé", "a fixé la caméra trois secondes sans sourire",
             "a dit « chat, is this real ? » au juge du tribunal administratif", "a fait un dab au moment exact du but",
             "a refusé la fanum tax d'un simple regard", "a fait un aura farming silencieux pendant tout le conseil de classe"]
EFFETS = ["La salle a explosé.", "Personne n'a osé rire, on a juste applaudi.", "J'ai vu un homme naître.",
          "Le silence était sacré.", "Même le directeur a validé.", "Les NPC ont arrêté leur boucle.", "L'Ohio s'est tu."]
TAGS = ["+2000 aura", "+1500 aura 🗿", "W énorme", "aura farming certifié", "+3000 aura, pas de débat", "🗿🗿", "W"]
def br(tier):
    s = p(SUJETS_BR)
    if tier == "anti":
        t = typo(p([
            f"{' '.join(S(['SKIBIDI', 'GYATT', 'OHIO', 'RIZZ', '6-7', 'FANUM TAX', 'SIGMA', 'MEWING', 'SUS', 'TRALALERO'], R.randint(4, 7)))} {p(['🗿🗿🗿', '😭😭', '💀💀💀'])} (j'ai {R.randint(31, 58)} ans)",
            f"j'ai fait le 6-7 à {p(['l’enterrement de mon oncle', 'mon entretien d’embauche', 'mon mariage', 'mon oral de bac'])} {p(['on m’a sorti', 'ma mère pleure', 'cé pas passé', 'L énorme'])}",
            f"jai fait payer la fanum tax à {p(['mon petit frère de 6 ans', 'ma grand-mère', 'un SDF', 'la cantinière'])} {p(['il pleure', 'elle a appelé ma mère', 'jsuis privé de wifi', 'mais jsuis sigma'])}",
            f"Mon CV : {p(['mewing (expert)', '6-7 (bilingue)', 'fanum tax (certifié)'])}, {p(['aura farming (natif)', 'rizz (niveau C2)', 'Ohio (LV2)'])}. Je comprends pas pourquoi on me rappelle pas.",
            f"Bonjour les jeunes ! {p(['Votre professeur', 'Votre maire', 'Votre conseiller bancaire'])} est très « {p(['rizz', 'Ohio', 'skibidi', 'sigma'])} » aujourd'hui ! Qui veut faire un dab ? 😎",
        ]))
        j = "Argot internet hors contexte et pathétique : aura négative."
    elif tier == "faible":
        t = typo(f"{p(['jsuis trop sigma', 'regardez mon mewing', 'jai trop d’aura', 'jsuis le roi du rizz', 'personne a mon aura'])} {p(['mais personne me répond', 'mais jai glissé dans le couloir', 'mais ma mère m’appelle mon poussin', 'mais jai 0 abonné', 'mais le prof ma mis une heure de colle'])} {p(['😔', '-500 aura', 'c normal ?', 'bon', ''])}".strip())
        j = "Aura revendiquée et démentie dans la même phrase."
    elif tier == "neutre":
        t = p([f"C'est quoi exactement le « {p(['6-7', 'fanum tax', 'mewing', 'scuba', 'aura farming', 'gyatt'])} » ? Mon {p(['fils', 'neveu', 'élève'])} en parle tout le temps.",
               f"Le mot « {p(['rizz', 'sigma', 'aura', 'skibidi'])} » vient d'internet et désigne, en gros, {p(['le charisme', 'un type de personnalité', 'le prestige', 'pas grand-chose de précis'])}.",
               f"Vu une vidéo de {p(['Tralalero Tralala', 'Tung Tung Tung Sahur', 'Bombardiro Crocodilo'])}. C'est {p(['un requin en baskets', 'un bout de bois avec une batte', 'un crocodile-avion'])}. D'accord."])
        j = "Description neutre de la culture internet."
    elif tier == "correcte":
        t = f"{p(['J’ai fait un scuba en sortant de la piscine', 'J’ai dit « six-sept » en réunion par réflexe', 'Pas de fanum tax sur mes frites aujourd’hui', 'Mon chat fait le mewing depuis sa naissance'])}, {p(['mes potes ont validé', 'personne a compris mais je reste fier', 'j’ai faim', 'c’est lui le vrai sigma'])}. {p(['+200 aura', '+100 aura', '🐈', 'W discret'])}"
        j = "Argot internet léger et autodérisoire, ça passe."
    elif tier == "forte":
        t = f"{s} {p(ACTES_TOP)}. {p(EFFETS)} {p(TAGS)}"
        j = "Argot internet bien placé, timing comique parfait."
    else:
        t = " ".join(S([
            f"{s} n'a pas dit un mot ; il a juste fait un mewing de quatre secondes, et l'Ohio entier s'est tu.",
            "Il ne farm pas l'aura : l'aura vient se faire farmer d'elle-même, par respect.",
            "Elle n'a pas de rizz : elle a un droit de veto sur le rizz des autres.",
            "Quand il fait le 6-7, ses mains montent lentement, comme une balance qui rend la justice.",
            "Il a dabé une seule fois, en 2016, et le geste est resté suspendu dans l'air depuis.",
            "Les casquettes tombent toutes seules quand il dit « no cap ».",
            "Tralalero Tralala lui a demandé un autographe ; il a signé d'un regard.",
            "On dit qu'il a mogué un miroir, et que le miroir a demandé une revanche.",
            "Même la fanum tax s'excuse quand elle passe devant son plateau.",
            "Il a regardé l'algorithme dans les yeux ; l'algorithme a baissé les siens.",
        ], R.choice([2, 3])))
        j = "Argot internet mythologique, absurde et parfaitement écrit."
    return t, j

# ====================================================================== PROSE / POÉSIE ORIGINALE
IMG = ["la pluie", "la mer", "la ville", "la nuit", "l'hiver", "le vent", "la neige", "les gares", "les phares", "l'aube"]
def prose(tier):
    a, b = S(IMG, 2)
    if tier == "faible":
        t = p([f"{a.capitalize()} tombe. Je suis triste. {b.capitalize()} aussi. Voilà.",
               f"Mon cœur est comme {a}, mais en plus mouillé, et en plus triste, et en plus moi.",
               f"Le soleil se couche comme un {p(['jaune d’œuf', 'ballon de foot', 'gros bonbon'])} sur {b}.",
               f"Je suis comme {a} : personne me comprend et ça m'énerve."])
        j = "Lyrisme plat ou métaphore involontairement comique."
    elif tier == "correcte":
        t = f"{a.capitalize()} ce matin, {b} ce soir, et entre les deux {p(['un café qui refroidit', 'une journée ordinaire', 'des gens pressés', 'une chanson qui tourne'])}. {p(['On appelle ça un mardi.', 'Ça me suffit.', 'Le bonheur a des horaires de bureau.'])}"
        j = "Petite prose douce et rythmée."
    elif tier == "forte":
        t = f"J'aime {a} parce qu'{p(['elle', 'il'])} ne demande rien, et {b} parce qu'{p(['elle', 'il'])} promet tout. Entre les deux, j'ai appris à {p(['attendre sans m’user', 'partir sans me retourner', 'me taire sans me perdre'])}."
        j = "Prose imagée et maîtrisée, belle présence."
    else:
        t = f"J'ai appris le silence auprès de {a} et la patience auprès de {b}. Le reste, je l'ai inventé, et personne n'a osé me dire que c'était faux."
        j = "Prose souveraine, images amples et autorité tranquille."
    return t.replace("parce qu'il", "parce qu'il").replace("parce qu'elle", "parce qu'elle"), j


def anti_divers():
    k = R.randrange(5)
    if k == 0:
        t = (f"ok donc tu préfères {p(['aller au ciné', 'sortir', 'manger un kebab', 'aller au foot', 'réviser'])} avec {p(['Kevin', 'ton coloc', 'tes potes', 'ce mec', 'ta cousine'])} plutôt qu'avec moi ? "
             f"{p(['super.', 'génial.', 'très bien.'])} {p(['non mais vas-y amuse-toi.', 'je dis rien.', 'tkt.'])} {p(['JE SUIS PAS FÂCHÉ.', 'je suis pas jaloux hein.', 'c’est pas grave.'])} {p(['😤', 'bonne soirée hein', 'je vais le dire à ta mère', 'de toute façon j’avais un truc'])}")
        j = "Jalousie passive-agressive puérile."
    elif k == 1:
        t = (f"{p(['Salut', 'Bonsoir', 'Hey', 'Wesh'])} {p(['ma belle', 'mademoiselle', 'la miss'])}, {p(['t’es trop charmante', 't’as un sourire de ouf', 't’as l’air pas comme les autres'])}. "
             f"{p(['T’as un 06 ?', 'Tu me donnes ton Snap ?', 'On se capte ?'])} … {p(['Pourquoi tu réponds pas ?', 'Allô ?', 'Ok.'])} "
             f"{p(['T’es moche de toute façon.', 'Hautaine.', 'Les filles comme toi finiront seules.', 'Bon tant pis, je retente demain.'])}")
        j = "Drague lourde qui vire à l'aigreur."
    elif k == 2:
        t = (f"Pendant que vous {p(['dormez', 'scrollez', 'faites la fête', 'pleurez pour votre ex', 'regardez des séries'])}, moi je {p(['me lève à 4h47', 'build mon empire', 'bois de l’eau citronnée en visualisant mes millions', 'vends des coques de téléphone en dropshipping', 'lis la quatrième de couverture d’un livre de développement perso'])}. "
             f"{p(['Les loups ne demandent pas la permission.', 'Bientôt la Lambo.', 'Vous allez regretter de m’avoir sous-estimé.', 'Personne croyait en moi sauf ma grand-mère.'])} {p(['🦁🔥', '🐺💯 #sigma', '#grindset', '👑'])}")
        j = "Grindset de façade, dominance autoproclamée et creuse."
    elif k == 3:
        t = (f"{p(['Aujourd’hui', 'Ce matin', 'Hier'])}, {p(['mon chat a vomi sur mon clavier', 'j’ai raté mon train', 'un inconnu m’a demandé l’heure', 'mon fils a refusé de manger ses brocolis'])}.\n\n"
             f"{p(['Et j’ai compris le vrai sens du leadership.', 'J’ai pleuré. Puis j’ai signé un client à 7 chiffres.', 'Ça m’a appris plus qu’un MBA.'])}\n\n"
             f"{p(['Je suis humble d’être aussi inspirant.', 'Likez si vous êtes d’accord 🙏', 'Agree ?', 'Je recrute (pas payé, mais formateur).'])} {p(['#leadership', '#humilité', '#mindset', '#résilience'])}")
        j = "Post LinkedIn égocentrique et absurde, cringe absolu."
    else:
        t = typo(f"{p(['first 🥇', 'qui regarde en 2026 ??', 'abonnez-vous à moi svp', '1 like = 1 prière', 'pov : toi qui lis ça'])} "
                 f"{p(['je suis à 12 abonnés aidez-moi 😭', 'check ma chaîne j’ai fait un remix', 'dédicace à mon frère', 'personne va lire ça mais bon', 'je like mon propre com'])}")
        j = "Mendicité numérique, présence nulle."
    return t, j

# ====================================================================== PLAN
def T(fn, *a): return lambda: fn(*a)
PLAN = {
    "Anti-Aura": [("politique", T(tribune, "anti"), 2), ("argot", T(br, "anti"), 4), ("moderne", T(bio, "anti"), 2),
                  ("moderne", T(nuit, "anti"), 2), ("moderne", anti_divers, 5)],
    "Aura Faible": [("politique", hem_faible, 3), ("politique", T(qag, "faible"), 2), ("politique", T(rep_ministre, "faible"), 3),
                    ("argot", T(br, "faible"), 3), ("moderne", T(bio, "faible"), 2), ("moderne", T(nuit, "faible"), 2),
                    ("quotidien", T(avis, "faible"), 1), ("prose", T(prose, "faible"), 1), ("classique", lambda: (p(VERS_RATES), "Vers de mirliton : rimes forcées et images ridicules."), 1)],
    "Aura Neutre": [("politique", hem_neutre, 3), ("politique", hem_proc, 4), ("politique", T(qag, "neutre"), 2),
                    ("politique", T(rep_ministre, "neutre"), 2), ("juridique", juridique, 3), ("quotidien", quotidien_neutre, 4),
                    ("quotidien", T(avis, "neutre"), 1), ("argot", T(br, "neutre"), 1), ("moderne", T(bio, "neutre"), 2)],
    "Aura Correcte": [("politique", hem_correcte, 3), ("politique", T(qag, "correcte"), 3), ("politique", T(rep_ministre, "correcte"), 2),
                      ("argot", T(br, "correcte"), 2), ("moderne", T(bio, "correcte"), 3), ("moderne", T(nuit, "correcte"), 2),
                      ("prose", T(prose, "correcte"), 2), ("classique", T(fable, "correcte"), 1), ("quotidien", T(avis, "correcte"), 1)],
    "Forte Aura": [("politique", T(tribune, "forte"), 3), ("politique", T(qag, "forte"), 3), ("politique", T(rep_ministre, "forte"), 3),
                   ("argot", T(br, "forte"), 4), ("moderne", T(bio, "forte"), 3), ("moderne", T(nuit, "forte"), 2),
                   ("prose", T(prose, "forte"), 2), ("classique", T(fable, "forte"), 1)],
    "Aura Légendaire": [("politique", T(tribune, "legend"), 3), ("classique", lambda: (p(MAX_TOP), "Maxime classique dense et bien frappée."), 3),
                        ("argot", T(br, "top"), 3), ("moderne", T(bio, "top"), 2), ("moderne", T(nuit, "top"), 2),
                        ("prose", T(prose, "top"), 2)],
    "Aura Divine": [("classique", lambda: (p(TIRADE_TOP), "Distique d'alexandrins tragiques, majesté absolue."), 2),
                    ("classique", lambda: (" ".join(S(MAX_TOP, 2)), "Deux maximes enchaînées, densité et autorité rares."), 3),
                    ("politique", lambda: (" ".join(S([tribune("legend")[0] for _ in range(4)], 2)), "Discours en deux temps, souffle et autorité souveraine."), 3),
                    ("argot", lambda: (" ".join(S([br("top")[0] for _ in range(3)], 2)), "Argot internet élevé au rang d'épopée."), 3),
                    ("prose", lambda: (prose("top")[0] + " " + p(["Les tempêtes ne crient pas : elles arrivent.", "On ne me cherche pas, on me reconnaît.", "Quand je me tais, les horloges hésitent."]), "Prose mythique, voix souveraine."), 2)],
}

def components(cname, style):
    lo, hi = next((l, h) for n, l, h in CLASSES if n == cname)
    for _ in range(5000):
        tgt = R.uniform(lo, hi)
        comp = {k: max(-100, min(100, round(tgt + OFF[style][k] + R.gauss(0, 9)))) for k in W}
        sc = round(sum(comp[k] * W[k] for k in W))
        if cls_of(sc) == cname: return comp, sc
    raise RuntimeError

# textes à exclure : test réel + anciens datasets
EXCL = set()
for f in ["aura_kit/data/test_reel.csv", "aura_kit/data/train_synthetique.csv"]:
    for r in csv.DictReader(open(f, encoding="utf-8-sig")): EXCL.add(sk(r["texte"]))

TARGET = 700
rows, seen = [], set(EXCL)
for cname, _, _ in CLASSES:
    gens = [(st, fn) for st, fn, w in PLAN[cname] for _ in range(w)]
    n, tries, per = 0, 0, Counter()
    while n < TARGET and tries < 400000:
        tries += 1
        st, fn = p(gens)
        t, j = fn()
        t = t.strip()
        if sk(t) in seen: continue
        seen.add(sk(t)); comp, sc = components(cname, st)
        rows.append(dict(texte=t, classe=cname, score=sc, justification=j, style=st, origine="v4_registres", **comp)); n += 1; per[st] += 1
    print(f"{cname:16s} {n} (essais {tries}) {dict(per)}")

def toks(t): return re.findall(r"\w+", t.lower())
TEST = [r["texte"] for r in csv.DictReader(open("aura_kit/data/test_reel.csv", encoding="utf-8-sig"))]
G6 = {tuple(w[i:i + 6]) for t in TEST for w in [toks(t)] for i in range(len(w) - 5)}
COURTS = {" ".join(toks(t)) for t in TEST if len(toks(t)) <= 6}
def fuite(t):
    w = toks(re.sub(r"\(.*?\)", "", t))
    return " ".join(w) in COURTS or any(tuple(w[i:i + 6]) in G6 for i in range(len(w) - 5))
avant = len(rows); rows = [r for r in rows if not fuite(r["texte"])]
print("retirés pour proximité avec le test :", avant - len(rows))
R.shuffle(rows)
with open("aura_dataset_v4.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["texte", "classe", "score", "justification", "style", "origine", "R", "S", "O", "B", "P"])
    w.writeheader(); w.writerows(rows)
print(len(rows), Counter(r["style"] for r in rows))
