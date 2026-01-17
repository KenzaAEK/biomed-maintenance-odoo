import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import time

print("🚀 Démarrage de l'entraînement optimisé...")
start_time = time.time()

# 1. CHARGEMENT
df = pd.read_csv('training_data.csv')
X = df['description']
y = df['category']

# 2. SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. VECTORISATION (LE SECRET EST ICI)
# max_features=1000 (au lieu de 100) : Le modèle connaît 10x plus de mots
# min_df=2 : Ignore les mots qui n'apparaissent qu'une seule fois (fautes de frappe, bruit)
print("🔠 Vectorisation...")
vectorizer = TfidfVectorizer(
    max_features=1000,      # <--- Augmenté de 100 à 1000
    ngram_range=(1, 2),     # Garde les paires de mots ("écran bleu")
    min_df=2,               # <--- Ignore les mots trop rares
    stop_words='english'    # (Optionnel) ou une liste de stop words français
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 4. ENTRAÎNEMENT
print("🌲 Entraînement du modèle...")
model = RandomForestClassifier(
    n_estimators=100,       # <--- 100 arbres pour plus de stabilité
    random_state=42,
    verbose=0               # <--- 0 pour ne pas polluer le terminal
)
model.fit(X_train_vec, y_train)

# 5. ÉVALUATION DÉTAILLÉE
print("\n📊 Résultats :")
accuracy = model.score(X_test_vec, y_test)
print(f"✅ Accuracy Globale: {accuracy:.2%}")

# Affiche les détails par catégorie pour voir où le modèle se trompe
print("\n🔍 Rapport détaillé :")
y_pred = model.predict(X_test_vec)
print(classification_report(y_test, y_pred))

# 6. SAUVEGARDE
joblib.dump(model, 'biomed_classifier.joblib')
joblib.dump(vectorizer, 'tfidf_vectorizer.joblib')

print(f"✅ Terminé en {time.time() - start_time:.2f} secondes.")