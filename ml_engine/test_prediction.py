import joblib

# 1. Charger le cerveau (le modèle et le vectoriseur)
model = joblib.load('biomed_classifier.joblib')
vectorizer = joblib.load('tfidf_vectorizer.joblib')

# 2. Phrases pièges (Ambiguës ou nouvelles)
nouveaux_tickets = [
    "L'écran est tout noir",                # Facile (Electronique ou Software ?)
    "Il y a une fuite d'huile importante",  # Facile (Hydraulique)
    "Le système est lent",                  # Facile (Software)
    "Ça fait un bruit bizarre",             # PIÈGE ! (Pourrait être Mécanique, Hydraulique ou Elec)
    "La souris ne clique plus"              # PIÈGE ! (Pas dans votre liste de composants ?)
]

# 3. Prédiction
X_new = vectorizer.transform(nouveaux_tickets)
predictions = model.predict(X_new)
probs = model.predict_proba(X_new)

print("🔍 RÉSULTATS DU CRASH TEST :")
print("-" * 30)
for text, pred, prob in zip(nouveaux_tickets, predictions, probs):
    confiance = max(prob) * 100
    print(f"Ticket : '{text}'")
    print(f" -> Prédiction : {pred} ({confiance:.1f}% de confiance)\n")