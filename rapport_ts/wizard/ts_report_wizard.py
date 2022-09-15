# -*- coding: utf-8 -*-

from odoo import models, fields, api



class TsReportWizard(models.TransientModel):
    _name = 'ts.report.wizard'
    _description = 'Rapport TS'

    chantier_id = fields.Many2one('project.project', string='Chantier', required=True)
    date_start = fields.Date('Date de début', required=True)
    date_end = fields.Date('Date de fin', required=True)

    def print_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'start_date': self.date_start,
                'end_date': self.date_end,
                'chantier_id': self.chantier_id.id,
            }}
        return self.env.ref('rapport_ts.report_ts').report_action(self, data=data)



