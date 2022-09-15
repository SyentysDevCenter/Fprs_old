# -*- coding: utf-8 -*-

from odoo import fields, models, api


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    type = fields.Selection([('a', 'Réel'), ('f', 'Prévu')], default='a')
    gen_account_id = fields.Many2one('account.account',string=u"Compte général",readonly=True)






