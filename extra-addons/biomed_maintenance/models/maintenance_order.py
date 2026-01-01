# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re

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
                             domain="[('product_id.categ_id.name', 'ilike', 'quipement')]") # 'quipement' gère E et É
    
    product_id = fields.Many2one('product.product', related='lot_id.product_id', string='Modèle', readonly=True)
    
    sale_order_id = fields.Many2one('sale.order', string='Commande Origine', compute='_compute_origin_sale', store=True)

    # --- 3. IA & DIAGNOSTIC ---
    description = fields.Text(string='Description', required=True)
    priority = fields.Selection([('0','Basse'), ('1','Normale'), ('2','Elevée'), ('3','URGENCE')], default='1', tracking=True)
    bio_hazard = fields.Boolean(string='Risque Bio', default=False, tracking=True)
    ai_analysis_log = fields.Text(string="Log IA", readonly=True)

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
        if not self.description: return
        text = self.description.lower()
        warnings = []
        
        # Regex pour éviter les faux positifs
        if any(re.search(p, text) for p in [r'fumée', r'feu\b', r'étincelle', r'brûlé', r'urgence', r'choc']):
            self.priority = '3'
            warnings.append("URGENCE DÉTECTÉE : Risque machine ou patient.")
            
        if any(re.search(p, text) for p in [r'sang', r'virus', r'bactérie', r'fluide', r'contamin']):
            self.bio_hazard = True
            warnings.append("RISQUE BIO DÉTECTÉ : Protocole EPI activé.")

        if warnings:
            self.ai_analysis_log = "\n".join(warnings)
            return {'warning': {'title': 'BioMed AI', 'message': "\n".join(warnings)}}

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