# -*- coding: utf-8 -*-

from odoo import fields, api, models
from odoo.exceptions import ValidationError



class Type(models.Model):
    _name = 'wbs.cost.type'

    name = fields.Char(u"Nom", required=True)
    model_id = fields.Many2one('ir.model',string='Objet', required=True,ondelete='cascade')
    field_id = fields.Many2one('ir.model.fields', string=u'Champ coût')
    account_field_id = fields.Many2one('ir.model.fields', string=u'Champ compte comptable')
    account_id = fields.Many2one('account.account', string=u'Compte comptable')
    product_field_id = fields.Many2one('ir.model.fields', string=u'Champ produit')

    # _sql_constraints = [
    #     ('model_uniq', 'unique (model_id)', "Model already exists !"),
    # ]

    @api.constrains('account_field_id', 'account_id')
    def _check_accont(self):
        for rec in self:
            if (not rec.account_field_id) and (not rec.account_id):
                raise ValidationError(u'Le Champ compte comptable ou bien Compte comptable doit être saisi!')

    @api.onchange('account_field_id')
    def onchange_account_field_id(self):
        if self.account_field_id:
            self.account_id = False


class SDP(models.Model):
    _name = 'wbs.cost.line'
    _rec_name = 'wbs_id'

    wbs_id = fields.Many2one('project.wbs', u"WBS", required=True)
    type_id = fields.Many2one('wbs.cost.type', u"Type", required=True)
    reference = fields.Reference(string='Document',
                                 selection='_reference_models', required=True)
    unit_cost = fields.Float(u'Coût unitaire')
    account_id = fields.Many2one('account.account', string=u'Compte comptable')
    product_id = fields.Many2one('product.product', string=u'Product')
    qty = fields.Float(u'Quatité', required=True)
    date = fields.Date(u'Date', required=True)
    cost = fields.Float(u'Coût total', compute="get_price")
    analytic_line_id = fields.Many2one('account.analytic.line', u'Analytical line', readonly=True)

    def name_get(self):
        res = []
        for line in self:
            name = line.type_id.name
            if line.reference:
                name += '/' + str(line.reference.name)
            res.append((line.id, name))
        return res

    def get_price(self):
        for record in self:
            record.cost = record.qty * record.unit_cost

    @api.model
    def _reference_models(self):
        types = self.env['wbs.cost.type'].search([])
        models = []
        for type in types:
            models.append((type.model_id.model, type.model_id.name))
        return models

    @api.onchange('reference')
    def onchange_reference(self):
        if self.reference:
            type = self.env['wbs.cost.type'].search([('model_id.model', '=', self.reference._name)])
            if type:
                account_id = False
                self.type_id = type.id
                if self.reference.read([type.field_id.name]):
                    self.unit_cost = self.reference.read([type.field_id.name])[0][type.field_id.name]
                print('ffffff', type.account_field_id.name)
                if type.account_field_id.name and self.reference.read([type.account_field_id.name]):
                    if self.reference.read([type.account_field_id.name])[0].get(type.account_field_id.name, False):
                        account_id = self.reference.read([type.account_field_id.name])[0][type.account_field_id.name]
                if not account_id:
                    if type.account_id:
                        account_id = type.account_id
                self.account_id = account_id
                if type.product_field_id.name and self.reference.read([type.product_field_id.name])[0].get(
                        type.product_field_id.name, False):
                    self.product_id = self.reference.read([type.product_field_id.name])[0][type.product_field_id.name]

    @api.onchange('type_id')
    def onchange_type(self):
        if self.reference:
            type = self.env['wbs.cost.type'].search([('model_id.model', '=', self.reference._name)])
            if type:
                self.type_id = type.id


class WBS(models.Model):
    _inherit = 'project.wbs'

    cost_line_ids = fields.One2many('wbs.cost.line', 'wbs_id', u'Cost lines')
    spd_validated = fields.Boolean(u"SDP validated")
    sdp_exist = fields.Boolean(u"SDP", compute='get_sdp_exist', store=True)
    analytic_line_id = fields.Many2one('account.analytic.line', u'Analytical line', readonly=True)

    def get_has_childs(self):
        for record in self:
            record.has_childs = len(record.child_ids) and True

    @api.depends('cost_line_ids')
    def get_sdp_exist(self):
        for record in self:
            record.sdp_exist = len(record.cost_line_ids) and True

    def validate_sdp(self):
        for record in self:
            if not record.product_id:
                raise ValidationError(u'Pas de produit de facturation!')
            account_line_obj = self.env['account.analytic.line']
            for line in record.cost_line_ids:
                analytic_data = {
                    'name': record.name,
                    'account_id': record.project_id.analytic_account_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_id.uom_id.id,
                    'date': line.date,
                    'unit_amount': line.qty,
                    'amount': -line.cost,
                    'wbs_id': record.id,
                    'general_account_id': line.account_id.id,
                }
                analytic_line_id = account_line_obj.create(analytic_data)
                analytic_line_id.type = 'f'
                analytic_line_id.amount = -line.cost
                line.analytic_line_id = analytic_line_id
            analytic_data = {
                'name': record.name,
                'account_id': record.project_id.analytic_account_id.id,
                'date': record.start_date,
                'unit_amount': record.qty,
                'amount': record.unit_price * record.qty,
                'wbs_id': record.id,
                'product_id': record.product_id.id,
                'product_uom_id': record.uom_id.id,
                'general_account_id': record.product_id.property_account_income_id.id,
            }
            analytic_line_id = account_line_obj.create(analytic_data)
            analytic_line_id.type = 'f'
            analytic_line_id.amount = record.unit_price * record.qty
            record.analytic_line_id = analytic_line_id
            record.spd_validated = True

    def edit_sdp(self):
        for record in self:
            for line in record.cost_line_ids:
                line.analytic_line_id.unlink()
            record.spd_validated = False
            record.analytic_line_id.unlink()

    def action_open_sdp(self):
        self.ensure_one()
        print(self.has_childs)
        sdp_ids = [sdp.id for sdp in self.cost_line_ids]
        action = {
            'name': 'SDP',
            'type': 'ir.actions.act_window',
            'res_model': 'wbs.cost.line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("id", "in", sdp_ids)],
            'context': {'default_wbs_id': self.id, 'default_date': self.start_date},
            'target': 'current',
        }
        return action
