# -*- coding: utf-8 -*-


from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    cost_timesheet = fields.Float('Coût horaire')

class HrJob(models.Model):
    _inherit = 'hr.job'

    cost = fields.Float(u'Coût')