# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fsm_task_ids = fields.One2many('project.task', 'fsm_sale_id', 'Interventions')
    fsm_task_count = fields.Integer('# Interventions', compute='compute_fsm_count', store=True)
    fsm_invoiceable = fields.Boolean('Dépanage facturable', compute='compute_fsm_invoiceable', store=True)
    bailleur_id = fields.Many2one('res.partner', 'Bailleur', tracking=True)
    en_attente = fields.Boolean('En attente', compute="compute_en_attente", store=True)
    depannage = fields.Boolean(default=False)
    conducteur_travaux_id = fields.Many2one('res.users', 'Conducteur des travaux', tracking=True)
    temps_passe = fields.Float(string='Feuille de temps (heures)', compute='compute_temps_passe', store=True)
    modalite_paiement_id = fields.Many2one('modalite.paiement', string='Modalité de paiement')
    n_siret = fields.Char(string='N° de SIRET', related='partner_id.siret', store=True)
    adress3 = fields.Text(string='Adresse 3')
    suivi_emetteur_bc = fields.Char(string='Suivi émetteur BC')
    date_debut = fields.Date(string='Date de début')
    date_fin = fields.Date(string='Date de fin')
    intervention_relle = fields.Date(string='intervention réel')
    tech1_id = fields.Many2one('hr.employee', string='Tech 1')
    tech2_id = fields.Many2one('hr.employee', string='Tech 2')
    interim_ssl = fields.Char(string='Intérim/SST')
    fsm_status_id = fields.Many2one('project.task.status', 'ETAT INTER')
    commande = fields.Boolean('Commande ?')
    factures_en_attente_validation = fields.Boolean('Factures en attente de validation', compute='compute_state',
                                                    store=True)
    factures_valides = fields.Boolean('Factures validées', compute='compute_state', store=True)
    technicien_id = fields.Many2one('res.users', compute='get_technicien', store=True)
    emetteur_bc_id = fields.Many2one('suivi.emetteur.bc', string='Suivi émetteur BC')
    corps_etat_id = fields.Many2one('corps.etat', string="Corps d'état")

    ##--##
    date_realisation = fields.Datetime(string="date realisation", compute='_compute_date_realisation', store=True)

    bilan_year = fields.Selection(string="BILAN FISCAL", selection=[('2020', '2020'),
                                                                    ('2021', '2021'),
                                                                    ('2022', '2022'),
                                                                    ('2023', '2023'),
                                                                    ('2024', '2024'),
                                                                    ('2025', '2025'),
                                                                    ('2026', '2026'),
                                                                    ('2027', '2027'),
                                                                    ('2028', '2028'),
                                                                    ('2029', '2029'),
                                                                    ('2030', '2030')], required=False)

    @api.depends('fsm_task_ids', 'fsm_task_ids.date_realisation')
    def _compute_date_realisation(self):
        for rec in self:
            if rec.fsm_task_ids:
                date_realisation_tasks = rec.fsm_task_ids.mapped('date_realisation')
                if date_realisation_tasks:
                    date_realisation_tasks = list(filter(None, date_realisation_tasks))
                    if date_realisation_tasks:
                        rec.date_realisation = max(date_realisation_tasks)
                    else:
                        rec.date_realisation = False
                else:
                    rec.date_realisation = False
            else:
                rec.date_realisation = False


    #def _create_invoices(self, grouped=False, final=False, date=None):
       # move = super(SaleOrder, self)._create_invoices()
       # if self.bilan_year:
         #   move.bilan_year = self.bilan_year

    def unlink(self):
        # deja sur odoo
        # if self.state in ['sent','sale']:
        #     raise ValidationError('Vous ne pouvez pas supprimer un bon de commande !')
        if self.fsm_task_ids:
            if any(l.fsm_state in ['confirm', 'done'] for l in self.fsm_task_ids):
                raise ValidationError(
                    'Vous ne pouvez pas supprimer un bon de commande si ses interventions sont validées ou faites !')
        return super(SaleOrder, self).unlink()

    @api.depends('fsm_task_ids', 'fsm_task_ids.user_id')
    def get_technicien(self):
        for r in self:
            if r.fsm_task_ids:
                fsm = r.fsm_task_ids.sorted(lambda u: u.create_date)
                r.technicien_id = fsm[0].user_id.id
            else:
                r.technicien_id = False

    @api.depends('invoice_ids', 'invoice_ids.state', 'invoice_count')
    def compute_state(self):
        for rec in self:
            if rec.invoice_ids:
                if any(f.state == 'attente' for f in rec.invoice_ids):
                    rec.factures_en_attente_validation = True
                else:
                    rec.factures_en_attente_validation = False

                if any(f.state != 'posted' for f in rec.invoice_ids):
                    rec.factures_valides = False
                else:
                    rec.factures_valides = True
            else:
                rec.factures_en_attente_validation = False
                rec.factures_valides = False

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            if self.partner_id.modalite_paiement_id:
                self.modalite_paiement_id = self.partner_id.modalite_paiement_id.id

    @api.onchange('chantier_id')
    def onchange_chantier_id(self):
        super(SaleOrder, self).onchange_chantier_id()
        if self.chantier_id and self.chantier_id.conducteur_travaux_id:
            self.conducteur_travaux_id = self.chantier_id.conducteur_travaux_id.id
        if self.chantier_id and self.chantier_id.bailleur_id:
            self.bailleur_id = self.chantier_id.bailleur_id.id

    @api.depends('fsm_task_ids', 'fsm_task_ids.effective_hours')
    def compute_temps_passe(self):
        for rec in self:
            somme = 0.0
            if rec.fsm_task_ids:
                somme = sum(l.effective_hours for l in rec.fsm_task_ids)

            rec.temps_passe = somme

    @api.model
    def create(self, vals):

        if vals.get('partner_id', False) and vals.get('client_order_ref', False):
            partner = vals['partner_id']
            ref = vals['client_order_ref']
            other_sales = self.env['sale.order'].search([('partner_id', '=', partner), ('client_order_ref', '=', ref)])
            if ref and len(other_sales) >= 1:
                raise ValidationError('La référence client du Bon de Commande doit être unique par client !!')
        if vals.get('depannage', False) and vals['depannage']:
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.fsm.seq')
        if vals.get('commande', False) and vals['commande']:
            vals['name'] = self.env['ir.sequence'].next_by_code('dev.com.seq')
        res = super(SaleOrder, self).create(vals)


        return res

    def write(self, values):
        result = super(SaleOrder, self).write(values)
        if values.get('interim_ssl'):
            for rec in self:
                if rec.fsm_task_ids:
                    rec.fsm_task_ids.write({'interim_ssl': rec.interim_ssl})

        if values.get('client_order_ref') or values.get('partner_id', False):
            for rec in self:
                other_sales = self.env['sale.order'].search(
                    [('partner_id', '=', rec.partner_id.id), ('client_order_ref', '=', rec.client_order_ref),
                     ('id', '!=', rec.id)])
                print('other sales', other_sales)
                if rec.client_order_ref and len(other_sales) >= 1:
                    raise ValidationError('La référence client du Bon de Commande doit être unique par client !!')
        return result

    @api.depends('fsm_task_ids', 'fsm_task_ids.en_attente')
    def compute_en_attente(self):
        for rec in self:
            if rec.depannage and (not rec.fsm_task_ids or any(l.en_attente for l in rec.fsm_task_ids)):
                rec.en_attente = True
            else:
                rec.en_attente = False

    def _prepare_invoice(self):
        if not self.fsm_invoiceable:
            raise UserError(
                "La commande %s ne peut pas être facturée avant la confirmation de toutes ses interventions" % (
                    self.name))
        res = super(SaleOrder, self)._prepare_invoice()
        if self.modalite_paiement_id:
            res['modalite_paiement_id'] = self.modalite_paiement_id.id
        res['bilan_year'] = self.bilan_year
         
        return res

    @api.depends('state', 'order_line.invoice_status', 'fsm_invoiceable')
    def _get_invoice_status(self):
        super(SaleOrder, self)._get_invoice_status()
        for rec in self:
            if rec.invoice_status == 'to invoice' and not rec.fsm_invoiceable:
                rec.invoice_status = 'no'

    @api.depends('fsm_task_ids', 'fsm_task_ids.fsm_state')
    def compute_fsm_invoiceable(self):
        for rec in self:
            if rec.depannage and (not rec.fsm_task_ids or any(f.fsm_state != 'confirm' for f in rec.fsm_task_ids)):
                rec.fsm_invoiceable = False
            else:
                rec.fsm_invoiceable = True

    @api.depends('fsm_task_ids')
    def compute_fsm_count(self):
        for rec in self:
            if rec.fsm_task_ids:
                rec.fsm_task_count = len(rec.fsm_task_ids)

            else:
                rec.fsm_task_count = 0

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        related_picking = self.mapped('picking_ids').filtered(lambda r: r.state not in ('cancel', 'done'))

        if related_picking:
            for line in related_picking.move_ids_without_package:
                line.write({'quantity_done': line.product_uom_qty})
                related_picking.button_validate()
        return res

    def validate_picking_create_invoice(self):
        self.ensure_one()
        if self.invoice_ids:
            if any(o.state in ('attente','posted') for o in self.invoice_ids):
                raise ValidationError('Ce bon de commande a déjà une facture en attente de validation ou validée !')

        related_picking = self.mapped('picking_ids')
        if related_picking:
            to_validate = related_picking.filtered(lambda r: r.state not in ('done', 'cancel'))
            if to_validate:
                for line in to_validate.move_ids_without_package:
                    line.write({'quantity_done': line.product_uom_qty})
                    to_validate.button_validate()

        action = self.env['ir.actions.act_window']._for_xml_id('sale.action_view_sale_advance_payment_inv')
        if self.invoice_status == 'no' and self.state == 'sale':
            action['context'] = {'default_advance_payment_method': 'percentage'}

        return action

    def fsm_task_action(self):
        self.ensure_one()
        context = {'fsm_mode': True,
                   'show_address': True,
                   # 'search_default_my_tasks': True,
                   # 'search_default_planned_future': True,
                   # 'search_default_planned_today': True,
                   'fsm_task_kanban_whole_date': False,
                   'default_is_fsm': True,
                   'default_fsm_sale_id': self.id,
                   'default_partner_id': self.partner_id.id,
                   'default_partner_email': self.partner_id.email,
                   'default_bailleur_id': self.bailleur_id and self.bailleur_id.id or False,

                   }
        superself = self.sudo()
        if self.sudo().chantier_id:
            context['default_project_id'] = superself.chantier_id and superself.chantier_id.id or False
            context["default_analytic_account_id"] = superself.chantier_id.analytic_account_id.id
        return {'type': 'ir.actions.act_window',
                'name': "Interventions",
                'res_model': 'project.task',
                'view_mode': 'tree,form,map,kanban,gantt,calendar,activity',
                # 'view_id': s,
                'domain': [('fsm_sale_id', '=', self.id)],
                'context': context,
                'target': 'current',
                }

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super(MailComposer, self).onchange_template_id(template_id, composition_mode, model, res_id)
        if res and res.get('value', False):
            if res['value'].get('partner_ids', False):
                if self.env.context.get('default_partner_ids', False):
                    res['value']['partner_ids'].extend(self.env.context['default_partner_ids'])
                partners = self.env['res.partner'].search([('id', 'in', res['value']['partner_ids'])])
                if partners:
                    partner_without_email = partners.filtered(lambda r: not r.email)
                    if partner_without_email:
                        for p in partner_without_email:
                            res['value']['partner_ids'].remove(p.id)
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ##--##
    date_realisation_so = fields.Datetime(string="Date realisation", related='order_id.date_realisation', store=True)

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        price = self.price_unit
        res = super(SaleOrderLine, self).product_uom_change()
        if price != self.price_unit:
            self.price_unit = price
