# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class AccountAccount(models.Model):
    _inherit = 'account.account'

    cree_fec = fields.Boolean(string="Créé FEC", default=False)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    cree_fec = fields.Boolean(string="Créé FEC", default=False)
