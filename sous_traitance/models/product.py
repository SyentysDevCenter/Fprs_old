# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    marge_soutraitance = fields.Float('Marge de sous-traitance', default=1)
