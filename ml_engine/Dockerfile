FROM python:3.10-slim

WORKDIR /app

# Copier les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier les fichiers du microservice
COPY . .

# Exposer le port
EXPOSE 5000

# Démarrer Flask
CMD ["python", "app.py"]