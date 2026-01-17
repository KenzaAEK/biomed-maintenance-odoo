from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

# Charger le modèle au démarrage
MODEL_PATH = 'biomed_classifier.joblib'
VECTORIZER_PATH = 'tfidf_vectorizer.joblib'

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("✅ Modèle chargé avec succès")
else:
    print("❌ ERREUR : Modèle non trouvé ! Exécutez train_model.py d'abord.")
    model = None
    vectorizer = None

# ENDPOINT DE PRÉDICTION
@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.json
        description = data.get('description', '').lower()
        
        if not description:
            return jsonify({'error': 'Description vide'}), 400
        
        # Vectorisation
        features = vectorizer.transform([description])
        
        # Prédiction
        category = model.predict(features)[0]
        probas = model.predict_proba(features)[0]
        confidence = float(max(probas))
        
        # Estimation durée (règles simplistes)
        durations = {
            'Electronique': 3.0,
            'Optique': 2.0,
            'Software': 1.5,
            'Hydraulique': 4.0
        }
        
        return jsonify({
            'category': category,
            'confidence': confidence,
            'suggested_duration': durations.get(category, 2.0)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ENDPOINT DE SANTÉ
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model_loaded': model is not None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)