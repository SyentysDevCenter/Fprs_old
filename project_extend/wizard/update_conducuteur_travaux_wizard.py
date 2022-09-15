# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models


class UpdateConducteurTrvxWizard(models.TransientModel):
    _name = "update.conducteur.travaux.wizard"
    _description = "Mise à jour des conducteurs de travaux des écritures analytiques"

    date = fields.Date('À partir du', required=True)
    conducteur_travaux_id = fields.Many2one('res.users', 'Conducteur des travaux')

    def update(self):
        all_account_analytic_line_ids = self.env['account.analytic.line'].sudo().search([])
        if all_account_analytic_line_ids:
            filtered_account_analytic_line_ids = all_account_analytic_line_ids.filtered(lambda x: x.date >= self.date)
            if filtered_account_analytic_line_ids:
                filtered_account_analytic_line_ids.write({'conducteur_travaux_id': self.conducteur_travaux_id.id})

