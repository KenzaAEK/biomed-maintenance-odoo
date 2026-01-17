# BioMed Maintenance Intelligente (Odoo 17 + IA) 🏥🤖

![Odoo Version](https://img.shields.io/badge/Odoo-17.0-purple) ![Python](https://img.shields.io/badge/Python-3.10-blue) ![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED) ![Status](https://img.shields.io/badge/Status-Prototype-green)

**Module Odoo de gestion de maintenance biomédicale avec architecture hybride (NLP Regex + Machine Learning).**

Ce projet a été réalisé dans le cadre du module **Génie Logiciel** (Projet ERP Odoo) à l'**ENSA Tanger**. Il vise à sécuriser les interventions techniques et optimiser le triage des pannes critiques grâce à une analyse sémantique automatisée [1].

## 📋 Contexte et Problématique

Dans le secteur médical, la sécurité des patients et des techniciens est critique. Les systèmes classiques de maintenance souffrent souvent de :
*   **Délais de triage :** Identifier une urgence vitale peut prendre plusieurs heures [2].
*   **Risques biologiques :** Les techniciens interviennent parfois sans EPI sur du matériel contaminé [2].
*   **Manque de traçabilité :** Difficulté à respecter la norme ISO 13485 [2].

**La Solution :** Une architecture hybride intégrant des règles de sécurité strictes (Regex) et un moteur d'intelligence artificielle (Random Forest) pour classifier les pannes [3].

## ✨ Fonctionnalités Clés

### 1. 🛡️ Sécurité & Triage Automatique (NLP Regex)
*   **Détection d'urgence vitale :** Analyse immédiate des descriptions pour détecter des mots-clés critiques (ex: "fumée", "feu", "étincelle") [4].
*   **Alerte Risque Biologique :** Détection automatique de contaminants (ex: "sang", "virus") déclenchant une alerte pour le port d'EPI [5].
*   **Action :** Force la priorité à ⭐⭐⭐ (Critique) et bloque le workflow si nécessaire.

### 2. 🧠 Classification Intelligente (Machine Learning)
*   Si aucun danger immédiat n'est détecté, un microservice ML analyse la description.
*   **Classification technique :** Catégorise la panne (Électronique, Optique, Logiciel, Hydraulique) [6].
*   **Prédiction :** Suggère une durée d'intervention et assigne le technicien compétent.
*   **Algorithme :** Random Forest (Accuracy ~95% sur dataset synthétique) [7].

### 3. 🏭 Intégration ERP Complète
*   **Lien Stock/Ventes :** Récupération automatique de la commande d'origine et du modèle via le Numéro de Série [8].
*   **Traçabilité ISO 13485 :** Utilisation du Chatter Odoo pour loguer chaque changement d'état, de priorité ou d'alerte [9].
*   **Workflow :** Gestion des états (Brouillon -> Confirmé -> En cours -> Terminé) [10].

## 🏗️ Architecture Technique

Le projet repose sur une architecture en **Microservices** découplés [11] :

1.  **Conteneur Odoo (Web) :** Gère l'interface utilisateur, la base de données et la logique métier (MVC).
2.  **Conteneur ML Engine (Flask API) :** Microservice Python hébergeant le modèle `scikit-learn` et exposant un endpoint REST `/predict`.

**Flux de données (Cascade Sécurisée) [12] :**
> Saisie Utilisateur -> Analyse Regex (Odoo) -> Si Sûr -> Appel API ML (Flask) -> Mise à jour Odoo.

## 🛠️ Stack Technologique

*   **ERP :** Odoo Community 17.0
*   **Langage :** Python 3.10.12
*   **Base de données :** PostgreSQL 15.3
*   **Virtualisation :** Docker & Docker Compose
*   **Machine Learning :** Scikit-learn, Pandas, Flask
*   **Architecture :** MVC (Model-View-Controller)

## 🚀 Installation et Démarrage

### Prérequis
*   Docker & Docker Compose installés [13].
*   Git.

### Étapes d'installation

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/votre-user/biomed-maintenance-odoo.git
    cd biomed-maintenance-odoo
    ```

2.  **Lancer l'environnement via Docker Compose [14] :**
    ```bash
    docker-compose up -d
    ```
    *Ceci démarrera les conteneurs `odoo-web`, `db` et `ml_engine`.*

3.  **Accéder à l'application :**
    *   Ouvrez votre navigateur sur `http://localhost:8069`.
    *   Identifiants par défaut (selon votre `docker-compose.yml`, souvent admin/admin).

4.  **Installer le module :**
    *   Activez le **Mode Développeur** (Paramètres > Activer le mode développeur) [15].
    *   Allez dans **Applications** > **Mettre à jour la liste des applications**.
    *   Recherchez `BioMed Maintenance Intelligente` et cliquez sur **Activer** [16].

## 🧪 Scénarios de Test

Pour vérifier le bon fonctionnement du module, vous pouvez tester les descriptions suivantes dans un nouvel *Ordre de Maintenance* :

| Description Saisie | Résultat Attendu | Technologie |
| :--- | :--- | :--- |
| *"De la fumée sort de l'appareil"* | 🚨 **Alerte Critique** + Priorité 3 étoiles | Regex (Sécurité) |
| *"Il y a des traces de sang sur la sonde"* | ☣️ **Risque Bio** + Case cochée auto | Regex (Sécurité) |
| *"L'écran reste noir au démarrage"* | 🔧 Catégorie: **Électronique** (Confiance > 90%) | Machine Learning |
| *"L'image est floue"* | 🔭 Catégorie: **Optique** | Machine Learning |

## 👤 Auteur

**ABOU-EL KASEM Kenza**
*   **Classe :** GINF3 - École Nationale des Sciences Appliquées (ENSA) Tanger
*   **Encadrant :** Prof. Hassan BADIR
*   **Année :** 2025-2026

---
*Ce projet est une preuve de concept (PoC) académique. Le modèle ML a été entraîné sur des données synthétiques.*
