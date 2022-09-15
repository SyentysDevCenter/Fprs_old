# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from odoo.tools import float_round


class report_ts(models.AbstractModel):
    _name = 'report.rapport_ts._report_ts'

    @api.model
    def _get_report_values(self, docids, data=None):
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        chantier = data['form']['chantier_id']
        date_start = fields.Date.from_string(start_date)
        date_end = fields.Date.from_string(end_date)
        chantier_id = self.env['project.project'].sudo().browse(chantier)
        if chantier_id:
            chantier_name = chantier_id.name
        docs= []
        project_timesheets = self.env['account.analytic.line'].search([('project_id', '=', chantier)])
        if project_timesheets:
            timing_timesheets = project_timesheets.filtered(lambda u: u.date and u.date >= date_start and u.date <= date_end)
            if timing_timesheets:
                employees = timing_timesheets.mapped('employee_id')
                if employees:
                    for emp in employees:
                        total_travaille = 0.0
                        total_intemperie = 0.0
                        total_absence = 0.0
                        emp_timesheets = timing_timesheets.filtered(lambda l: l.employee_id.id == emp.id)
                        if emp_timesheets:
                            timsheet_travaille = emp_timesheets.filtered(lambda u: u.absence == False and u.intemperie == False)
                            if timsheet_travaille:
                                total_travaille = sum(timsheet_travaille.mapped('unit_amount'))
                            timsheet_absence = emp_timesheets.filtered(lambda u: u.absence == True and u.intemperie == False)
                            if timsheet_absence:
                                total_absence = sum(timsheet_absence.mapped('unit_amount'))

                            timsheet_intemperie = emp_timesheets.filtered(lambda u: u.absence == False and u.intemperie == True)
                            if timsheet_intemperie:
                                total_intemperie = sum(timsheet_intemperie.mapped('unit_amount'))

                            docs.append({
                                        'matricule': emp.matricule,
                                        'employee_name': emp.name,
                                        'heures_travailles': total_travaille,
                                        'heures_absence': total_absence,
                                        'heures_intemperie': total_intemperie,
                                        })

        total_heures_travailles = 0.0
        total_heures_absence = 0.0
        total_heures_intemperie = 0.0
        if docs:
            for t in docs:
                total_heures_travailles += t['heures_travailles']
                total_heures_absence += t['heures_absence']
                total_heures_intemperie += t['heures_intemperie']

        return {
            'docs': docs,
            'data': data,
            'docids': docids,
            'chantier_name': chantier_name,
            'date_start': date_start.strftime('%d/%m/%Y'),
            'date_end': date_end.strftime('%d/%m/%Y'),
            'company': self.env.user.company_id.name,
            'today': fields.Date.today().strftime('%d/%m/%Y'),
            'total_heures_travailles': total_heures_travailles,
            'total_heures_absence': total_heures_absence,
            'total_heures_intemperie': total_heures_intemperie,

        }
