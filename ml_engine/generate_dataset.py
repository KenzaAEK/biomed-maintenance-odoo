import pandas as pd
import random

# Number of examples to generate per category
SAMPLES_PER_CATEGORY = 500

# ---------------------------------------------------------
# 1. VOCABULARY DEFINITION
# We separate "Components" (Nouns) from "Issues" (Symptoms)
# ---------------------------------------------------------

vocab = {
    'Electronique': {
        'components': [
            "alimentation", "batterie", "carte mère", "écran", "condensateur", 
            "fusible", "câble USB", "transformateur", "disjoncteur", "LED", 
            "bouton power", "circuit imprimé", "résistance", "connecteur de charge"
        ],
        'issues': [
            "ne s'allume plus", "fume", "est brûlant", "a grillé", "fait des étincelles", 
            "ne charge pas", "clignote en rouge", "sent le brûlé", "est en court-circuit", 
            "a explosé", "ne répond plus", "surchauffe", "est noirci", "a fondu"
        ]
    },
    'Optique': {
        'components': [
            "lentille", "objectif", "capteur", "mise au point", "zoom", "miroir", 
            "prisme", "viseur", "diaphragme", "obturateur", "image", "focus"
        ],
        'issues': [
            "est flou", "est rayé", "a des taches", "est bloqué", "est cassé", 
            "est désaligné", "est sale", "ne fait plus le point", "est déformé", 
            "a de la poussière interne", "est voilé", "manque de netteté"
        ]
    },
    'Software': {
        'components': [
            "logiciel", "système", "application", "mise à jour", "base de données", 
            "serveur", "interface", "driver", "licence", "connexion", "windows", "linux"
        ],
        'issues': [
            "a planté", "est figé", "affiche un écran bleu", "ne démarre pas", 
            "est corrompu", "est lent", "a crashé", "renvoie une erreur 404", 
            "demande un mot de passe", "a expiré", "boucle à l'infini", "ne répond pas"
        ]
    },
    'Hydraulique': {
        'components': [
            "pompe", "tuyau", "valve", "joint", "réservoir", "piston", "vérin", 
            "filtre", "manomètre", "raccord", "vanne", "circuit d'huile"
        ],
        'issues': [
            "fuit", "perd de la pression", "est bouché", "fait un bruit de gargouillis", 
            "est percé", "est grippé", "n'aspire plus", "refoule du liquide", 
            "a éclaté", "vibre énormément", "est sec", "siffle fort"
        ]
    }
}

# ---------------------------------------------------------
# 2. SENTENCE TEMPLATES
# These simulate how real humans write support tickets.
# {c} = component, {i} = issue
# ---------------------------------------------------------
templates = [
    "Le {c} {i}.",
    "J'ai un problème, le {c} {i} complètement.",
    "Attention, {c} qui {i} !",
    "Erreur détectée : {c} {i}.",
    "Il semble que le {c} {i} depuis ce matin.",
    "Panne critique : {c} {i}.",
    "Le client signale que le {c} {i}.",
    "Impossible d'utiliser la machine, le {c} {i}.",
    "Défaut sur {c} : il {i}.",
    "Gros souci avec le {c}, il {i}."
]

# ---------------------------------------------------------
# 3. GENERATION ENGINE
# ---------------------------------------------------------
data_rows = []

for category, words in vocab.items():
    for _ in range(SAMPLES_PER_CATEGORY):
        # Pick random component and random issue from this category
        comp = random.choice(words['components'])
        issue = random.choice(words['issues'])
        template = random.choice(templates)
        
        # Create the sentence
        sentence = template.format(c=comp, i=issue)
        
        # Add a little noise (optional): Randomly lowercase sometimes
        if random.random() > 0.5:
            sentence = sentence.lower()
            
        data_rows.append({
            'description': sentence,
            'category': category
        })

# ---------------------------------------------------------
# 4. SAVE
# ---------------------------------------------------------
df = pd.DataFrame(data_rows)

# Shuffle the dataset
df = df.sample(frac=1).reset_index(drop=True)

print(df.head(10)) # Show preview
print(f"\n✅ Generated {len(df)} examples total.")
print(f"✅ Distribution:\n{df['category'].value_counts()}")

df.to_csv('training_data.csv', index=False, encoding='utf-8')