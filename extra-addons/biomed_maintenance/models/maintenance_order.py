# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re
import requests
import logging

_logger = logging.getLogger(__name__)

class BiomedMaintenanceOrder(models.Model):
    _name = 'biomed.maintenance.order'
    _description = 'Ordre de Maintenance Biomédical'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_scheduled asc'

    # --- 1. IDENTIFICATION ---
    name = fields.Char(string='Référence', required=True, copy=False, readonly=True, 
                       default=lambda self: _('Nouveau'))
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('in_progress', 'En cours'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string='Statut', default='draft', tracking=True)

    # --- 2. LIAISON PARTIE 1 ---
    partner_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    
    lot_id = fields.Many2one('stock.lot', string='Numéro de Série', required=True, tracking=True,
                             domain="[('product_id.categ_id.name', 'ilike', 'quipement')]")
    
    product_id = fields.Many2one('product.product', related='lot_id.product_id', string='Modèle', readonly=True)
    
    sale_order_id = fields.Many2one('sale.order', string='Commande Origine', compute='_compute_origin_sale', store=True)

    # --- 3. IA & DIAGNOSTIC ---
    description = fields.Text(string='Description', required=True)
    priority = fields.Selection([('0','Basse'), ('1','Normale'), ('2','Elevée'), ('3','URGENCE')], default='1', tracking=True)
    bio_hazard = fields.Boolean(string='Risque Bio', default=False, tracking=True)
    ai_analysis_log = fields.Text(string="Log IA", readonly=True)
    
    # ========== NOUVEAU CHAMP ML ==========
    category = fields.Selection([
        ('Electronique', 'Électronique'),
        ('Optique', 'Optique'),
        ('Software', 'Logiciel'),
        ('Hydraulique', 'Hydraulique')
    ], string='Catégorie Technique', tracking=True)

    # --- 4. PLANIFICATION ---
    technician_id = fields.Many2one('res.users', string='Technicien', tracking=True)
    date_scheduled = fields.Datetime(string='Date Prévue')
    duration = fields.Float(string='Durée (h)', default=1.0)
    intervention_report = fields.Text(string="Rapport")
    part_ids = fields.One2many('biomed.maintenance.part', 'maintenance_id', string="Pièces")

    # --- LOGIQUE MÉTIER ---
    @api.depends('lot_id', 'partner_id')
    def _compute_origin_sale(self):
        for record in self:
            if record.partner_id and record.product_id:
                sale = self.env['sale.order'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('state', 'in', ['sale', 'done']),
                    ('order_line.product_id', '=', record.product_id.id)
                ], limit=1, order='date_order desc')
                record.sale_order_id = sale
            else:
                record.sale_order_id = False

    @api.onchange('description')
    def _onchange_ai_triage(self):
        # 1. Sécurité : Si la description est vidée, on réinitialise les alertes
        if not self.description:
            self.priority = '1'
            self.bio_hazard = False
            self.ai_analysis_log = False
            self.category = False
            return

        text = self.description.lower()
        warnings = []
        
        # ========== COUCHE 1 : REGEX (Hard Security) ==========
        # Priorité 3 (Urgence Vitale / Danger Incendie)
        critical_patterns = [r'fumée', r'feu\b', r'étincelle', r'brûlé', r'explosion', r'choc', r'court-circuit']
        # Priorité 2 (Panne Bloquante / Inutilisable)
        high_patterns = [r'panne', r'bloqué', r'erreur', r'anomalie', r'dysfonctionnement', r'cassé', r'ne démarre plus']
        # Risque Bio (Indépendant de la priorité technique)
        bio_patterns = [r'sang', r'virus', r'bactérie', r'fluide', r'contamin', r'covid', r'exposition']

        # LOGIQUE DE TRIAGE TECHNIQUE
        new_priority = '1'  # Par défaut : Normale (1 étoile)
        
        if any(re.search(p, text) for p in critical_patterns):
            new_priority = '3'  # Critique (3 étoiles)
            warnings.append("🚨 ALERTE CRITIQUE : Risque d'incendie ou d'accident majeur détecté.")
        elif any(re.search(p, text) for p in high_patterns):
            new_priority = '2'  # Élevée (2 étoiles)
            warnings.append("⚠️ PANNE MAJEURE : L'équipement est hors-service et nécessite une intervention rapide.")
        
        self.priority = new_priority

        # LOGIQUE DE RISQUE BIOLOGIQUE
        if any(re.search(p, text) for p in bio_patterns):
            self.bio_hazard = True
            warnings.append("☣️ RISQUE BIOLOGIQUE : Présence de contaminants suspectée. Protocole EPI requis.")
        else:
            self.bio_hazard = False

        # ========== COUCHE 2 : MACHINE LEARNING (Soft Intelligence) ==========
        if len(self.description) > 15:
            try:
                response = requests.post(
                    'http://ml_engine:5000/predict',
                    json={'description': self.description},
                    timeout=3
                )
                
                if response.status_code == 200:
                    ml_result = response.json()
                    
                    # Auto-complétion de la catégorie
                    self.category = ml_result.get('category')
                    
                    # Suggestion de durée (si pas déjà remplie)
                    if not self.duration or self.duration == 1.0:
                        self.duration = ml_result.get('suggested_duration', 1.0)
                    
                    # Ajout du log ML
                    confidence_pct = ml_result.get('confidence', 0) * 100
                    warnings.append(f"🤖 ML : {self.category} ({confidence_pct:.0f}% confiance)")
                    
                    _logger.info(f"ML Prediction: {ml_result}")
                
                else:
                    _logger.warning(f"ML API returned status {response.status_code}")
            
            except requests.exceptions.RequestException as e:
                # Si le microservice est down, on continue avec Regex seul
                _logger.warning(f"ML service unavailable: {e}")
                pass

        # ========== FEEDBACK UTILISATEUR ==========
        if warnings:
            self.ai_analysis_log = "\n".join(warnings)
            return {
                'warning': {
                    'title': 'Analyse BioMed AI Security',
                    'message': "\n".join(warnings) + "\n\nLes paramètres de sécurité ont été ajustés automatiquement."
                }
            }
        else:
            self.ai_analysis_log = False

    # --- WORKFLOW (LES BOUTONS) ---
    @api.model
    def create(self, vals):
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('biomed.maintenance.order') or _('Nouveau')
        return super(BiomedMaintenanceOrder, self).create(vals)

    def action_confirm(self):
        self.state = 'confirmed'

    def action_start(self):
        self.state = 'in_progress'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        for record in self:
            if record.state == 'done':
                raise UserError("Impossible d'annuler une intervention terminée.")
            record.state = 'cancelled'


class BiomedMaintenancePart(models.Model):
    _name = 'biomed.maintenance.part'
    _description = 'Pièce Détachée'
    maintenance_id = fields.Many2one('biomed.maintenance.order')
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(default=1.0)
    note = fields.Char()