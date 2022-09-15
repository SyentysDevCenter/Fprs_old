# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Project(models.Model):
    _inherit = 'project.project'


    revenu_prevu_amount = fields.Float(compute="compute_cost_amount", store=True, string="Revenu prévu")
    marge_souhaite = fields.Float('Marge souhaitée', default=40.0)
    montant_marche_actualise = fields.Float('Montant du marché actualisé')
    initial_cost = fields.Float(string="Coût initial",  required=False)
    initial_income = fields.Float(string="Revenue initial",  required=False)


    @api.depends('forecast_analytic_line_ids', 'forecast_analytic_line_ids.amount')
    def compute_cost_amount(self):
        for rec in self:
            update = False
            if rec.forecast_analytic_line_ids:
                if rec.revenu_prevu_amount == rec.montant_marche_actualise or rec.montant_marche_actualise == 0.0:
                    update = True
                rec.revenu_prevu_amount = sum(l.amount for l in rec.forecast_analytic_line_ids.filtered(lambda r: r.amount>0))
                if update:
                    rec.montant_marche_actualise = rec.revenu_prevu_amount

            else:
                rec.revenu_prevu_amount =0


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'


    account_journal_id = fields.Many2one('account.journal', related='move_id.journal_id', store=True)