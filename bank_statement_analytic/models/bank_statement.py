# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Code chantier')

    @api.model
    def _prepare_counterpart_move_line_vals(self, counterpart_vals, move_line = None):
        res = super()._prepare_counterpart_move_line_vals(counterpart_vals, move_line = move_line)
        if self.analytic_account_id:
            res['analytic_account_id'] = self.analytic_account_id.id
        return res


