# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re

class BiomedMaintenanceOrder(models.Model):
    """
    Modèle principal pour la gestion des ordres de maintenance.
    Intègre une logique d'IA pour le triage et une liaison forte avec les stocks (Partie 1).
    """
    _name = 'biomed.maintenance.order'
    _description = 'Ordre de Maintenance Biomédical'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Active le "Chatter" (Historique complet)
    _order = 'priority desc, date_scheduled asc'

    # ==========================================================================
    # 1. IDENTIFICATION & WORKFLOW
    # ==========================================================================
    name = fields.Char(
        string='Référence',
        required=True, copy=False, readonly=True, index=True,
        default=lambda self: _('Nouveau')
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', tracking=True, group_expand='_expand_states')

    # ==========================================================================
    # 2. LIAISON TECHNIQUE AVEC LA PARTIE 1 (OPTIMISATION MAJEURE)
    # ==========================================================================
    # On lie au Client (res.partner) créé en Partie 1
    partner_id = fields.Many2one(
        'res.partner', string='Client / Établissement',
        required=True, tracking=True,
        domain="[('customer_rank', '>', 0)]"
    )

    # OPTIMISATION : On cible le Numéro de Série (stock.lot) et non juste le produit.
    # Cela permet de savoir exactement quel appareil (ex: SN-001) est en panne.
    lot_id = fields.Many2one(
        'stock.lot', string='Numéro de Série (Appareil)',
        required=True, tracking=True,
        domain="[('product_id.categ_id.name', 'ilike', 'Équipements')]", # Filtre sur catégorie Partie 1
        help="Sélectionnez l'unité spécifique vendue (Traçabilité S/N)"
    )

    # Champ calculé automatiquement via le lot_id
    product_id = fields.Many2one(
        'product.product', string='Modèle',
        related='lot_id.product_id', store=True, readonly=True
    )

    # OPTIMISATION : Lien automatique vers le Bon de Livraison ou Commande d'origine
    sale_order_id = fields.Many2one(
        'sale.order', string='Commande d\'Origine',
        compute='_compute_origin_sale', store=True,
        help="Retrouvé automatiquement via l'historique du client"
    )

    # ==========================================================================
    # 3. IA & ANALYSE DE CRITICITÉ (NLP BASIQUE)
    # ==========================================================================
    description = fields.Text(
        string='Description du Problème', 
        required=True,
        help="Décrivez les symptômes. L'IA analysera ce texte."
    )

    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Élevée'),
        ('3', 'CRITIQUE (Urgence Vitale)')
    ], string='Priorité', default='1', tracking=True)

    bio_hazard = fields.Boolean(
        string='Risque Biologique', default=False, tracking=True,
        help="Coché automatiquement si contamination détectée (Sang, Virus...)"
    )

    ai_analysis_log = fields.Text(string="Log Analyse IA", readonly=True)

    # ==========================================================================
    # 4. GESTION DE L'INTERVENTION
    # ==========================================================================
    technician_id = fields.Many2one('res.users', string='Technicien', tracking=True)
    date_scheduled = fields.Datetime(string='Date Prévue', tracking=True)
    duration = fields.Float(string='Durée (Heures)', default=1.0)
    
    # Gestion des pièces détachées consommées
    part_ids = fields.One2many('biomed.maintenance.part', 'maintenance_id', string="Pièces Consommées")

    # ==========================================================================
    # MÉTHODES : INTELLIGENCE & AUTOMATISATION
    # ==========================================================================

    @api.depends('lot_id', 'partner_id')
    def _compute_origin_sale(self):
        """
        Tente de retrouver la commande de vente de la Partie 1 qui correspond 
        au client et au produit du numéro de série sélectionné.
        """
        for record in self:
            if record.partner_id and record.product_id:
                # Recherche d'une commande confirmée pour ce client et ce produit
                sale = self.env['sale.order'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('state', 'in', ['sale', 'done']),
                    ('order_line.product_id', '=', record.product_id.id)
                ], limit=1, order='date_order desc') # Prend la plus récente
                record.sale_order_id = sale
            else:
                record.sale_order_id = False

    @api.onchange('description')
    def _onchange_ai_triage(self):
        """
        🤖 Moteur d'IA (NLP) : Analyse la description en temps réel.
        Détecte les mots-clés via Regex pour éviter les erreurs.
        """
        if not self.description:
            return

        text = self.description.lower()
        warnings = []
        
        # 1. Dictionnaire de criticité
        critical_patterns = [r'fumée', r'feu\b', r'étincelle', r'brûlé', r'urgence', r'arrêt.*cardiac', r'patient']
        bio_patterns = [r'sang', r'virus', r'bactérie', r'fluide', r'contamin', r'covid']

        # 2. Analyse Urgence Technique
        is_critical = any(re.search(pat, text) for pat in critical_patterns)
        if is_critical:
            self.priority = '3'
            warnings.append("URGENCE DÉTECTÉE : Risque machine ou patient identifié.")

        # 3. Analyse Risque Biologique
        is_bio = any(re.search(pat, text) for pat in bio_patterns)
        if is_bio:
            self.bio_hazard = True
            warnings.append("RISQUE BIO DÉTECTÉ : Présence possible de contaminants.")

        # 4. Feedback Utilisateur (UX)
        if warnings:
            self.ai_analysis_log = "\n".join(warnings)
            return {
                'warning': {
                    'title': 'BioMed AI Security',
                    'message': "\n".join(warnings) + "\n\nLes paramètres de sécurité ont été mis à jour automatiquement."
                }
            }

    # ==========================================================================
    # WORKFLOW (BOUTONS D'ACTION)
    # ==========================================================================

    @api.model
    def create(self, vals):
        # Génération du numéro de séquence (ex: MO/2026/001)
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('biomed.maintenance.order') or _('Nouveau')
        return super(BiomedMaintenanceOrder, self).create(vals)

    def action_confirm(self):
        if not self.technician_id:
            raise UserError("Veuillez assigner un technicien avant de confirmer.")
        self.state = 'confirmed'

    def action_start(self):
        self.state = 'in_progress'

    def action_done(self):
        """
        Clôture de l'intervention.
        Idée Optimisation : On pourrait ici décrémenter le stock des pièces utilisées.
        """
        if self.bio_hazard and not self.description:
             raise UserError("Une maintenance à risque bio nécessite un rapport détaillé.")
        self.state = 'done'


class BiomedMaintenancePart(models.Model):
    """
    Sous-modèle pour lister les pièces détachées utilisées pendant la réparation.
    """
    _name = 'biomed.maintenance.part'
    _description = 'Pièces de Maintenance'

    maintenance_id = fields.Many2one('biomed.maintenance.order', string="Ordre")
    product_id = fields.Many2one('product.product', string="Pièce", required=True)
    quantity = fields.Float(string="Qté", default=1.0)
    note = fields.Char(string="Commentaire")