from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_garantie_retenue = fields.Boolean(string="Garantie retenue")
