# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    soustraitance = fields.Boolean("Sous traitance")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    requisition_id = fields.Many2one('purchase.requisition', 'Convention de soustraitance')


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    sale_line_id = fields.Many2one('sale.order.line', 'Commande')
    sale_price = fields.Float(related='sale_line_id.price_unit', string='Prix de vente',  store=True)