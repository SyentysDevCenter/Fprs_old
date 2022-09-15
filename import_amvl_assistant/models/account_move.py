# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class AccountMove(models.Model):
    _inherit = 'account.move'

    importe_fec = fields.Boolean(string="Importée FEC", default=False)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fec_matching_number = fields.Char(help="Matching code that is used in FEC import for reconciliation")
    importe_fec = fields.Boolean(string="Importée FEC", default=False)


