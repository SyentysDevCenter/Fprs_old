from odoo import api, fields, models


class ProjectFinancierReportWizard(models.TransientModel):
    _name = 'project.financier.report.wizard'

    from_date = fields.Date(string="Date de Debut", required=False)
    to_date = fields.Date(string="Date de Fin", required=False)
    project_id = fields.Many2one(comodel_name="project.project", string="projet", required=False)

    def print_report(self):
        print('Print Report')
        # check date
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise Warning('Vous devez choisir une date valide')

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': self.from_date,
                'to_date': self.to_date,
                'project_id': [self.project_id.id],
            }}
        return self.env.ref('project_report.action_report_project_financier').report_action(self, data=data)
