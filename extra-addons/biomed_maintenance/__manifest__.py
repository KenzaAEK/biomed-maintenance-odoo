# -*- coding: utf-8 -*-
{
    # ==========================================================================
    # IDENTITÉ DU MODULE
    # ==========================================================================
    'name': 'BioMed Maintenance Intelligente',
    'version': '1.0.0',
    'category': 'Services/Medical',  # Catégorie précise pour le filtrage
    'author': 'ABOU-EL KASEM Kenza - ENSA Tanger',
    'website': 'https://github.com/KenzaAEK/biomed-maintenance-odoo.git',
    'license': 'LGPL-3',

    # ==========================================================================
    # DESCRIPTION COMMERCIALE (Apparaît dans le store Odoo)
    # ==========================================================================
    'summary': 'Gestion des maintenances biomédicales avec analyse IA de criticité',
    'description': """
Module de gestion spécialisée pour les interventions sur équipements médicaux BioMed Tanger.

Fonctionnalités Clés :
----------------------
* 🤖 **Intelligence Artificielle** : Analyse sémantique (NLP) des pannes pour détecter la criticité.
* ☣️ **Sécurité** : Détection automatique du risque biologique et alertes EPI.
* 🔗 **Intégration ERP (Partie 1)** : Lien direct avec les Ventes et les Numéros de Série.
* 📋 **Conformité** : Workflow de validation et traçabilité complète des interventions.
    """,

    # ==========================================================================
    # DÉPENDANCES (LE PONT VERS LA PARTIE 1)
    # ==========================================================================
    'depends': [
        'base',     # Socle technique
        'product',  # Pour les équipements
        'sale',     # Pour lier aux commandes clients (Partie 1)
        'stock',    # Pour les numéros de série (Partie 1)
        'mail',     # Pour le Chatter (Historique et discussion)
    ],

    # ==========================================================================
    # CHARGEMENT DES DONNÉES (ORDRE CRITIQUE !)
    # ==========================================================================
    'data': [
        # 1. SÉCURITÉ : Toujours en premier pour définir "qui a le droit"
        'security/ir.model.access.csv',

        # 2. DONNÉES TECHNIQUES : La séquence doit exister avant d'être utilisée
        'data/maintenance_sequence.xml',

        # 3. INTERFACE UTILISATEUR (VUES) : Charge les menus et formulaires
        'views/maintenance_order_views.xml',
    ],

    # ==========================================================================
    # CONFIGURATION TECHNIQUE
    # ==========================================================================
    'demo': [],
    'installable': True,
    'application': True,   # True = Apparaît comme une App principale (avec icône)
    'auto_install': False,
    'assets': {
        # pour ajouter du CSS/JS personnalisé plus tard.
    }
}