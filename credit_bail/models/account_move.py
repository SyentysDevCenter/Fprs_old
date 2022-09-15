from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    credit_bail_id = fields.Many2one(comodel_name="account.credit.bail")
