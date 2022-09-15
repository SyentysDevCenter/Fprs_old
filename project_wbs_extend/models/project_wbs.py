# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectWbs(models.Model):
    _inherit = 'project.wbs'

    numero_debourse = fields.Char('Numero en deboursé')
    price_suggest = fields.Float('Prix de vente proposé', compute='compute_suggested_price', store=True)

    @api.depends('cost_line_ids', 'cost_line_ids.sale_price_total')
    def compute_suggested_price(self):
        for rec in self:
            rec.price_suggest = sum(l.sale_price_total for l in rec.cost_line_ids)

    def apply_suggested(self):
        for rec in self:
            rec.unit_price = rec.price_suggest


class SDP(models.Model):
    _inherit = 'wbs.cost.line'

    sale_coef = fields.Float('Coefficient de vente', default=1)
    sale_price_unit = fields.Float('Prix de vente unitaire', compute='compute_sale_price', store=True)
    sale_price_total = fields.Float('Prix de vente total', compute='compute_sale_price', store=True)

    @api.depends('sale_coef', 'unit_cost', 'qty')
    def compute_sale_price(self):
        for rec in self:
            rec.sale_price_unit = rec.unit_cost * rec.sale_coef
            rec.sale_price_total = rec.unit_cost * rec.sale_coef * rec.qty

