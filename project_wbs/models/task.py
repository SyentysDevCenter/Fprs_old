# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Task(models.Model):
    _inherit = 'project.task'
    _order = 'wbs_code'

    wbs_id = fields.Many2one('project.wbs', u"WBS")
    wbs_code = fields.Char(related='wbs_id.code', string=u"Code WBS", store=True, readonly=True)
    date_start = fields.Date()
    date_deadline = fields.Date(string='Date échéance', index=True, copy=True)
    actual_count = fields.Integer(compute="get_actual_budget_count", string=u"# Actual", store=True)
    budget_count = fields.Integer(compute="get_actual_budget_count", string=u"# Budget", store=True)

    cost = fields.Float(u"Coût", compute="get_cost_budget", store=True)
    budget = fields.Float(u"Budget", compute="get_cost_budget", store=True)

    actual_timesheet_ids = fields.One2many('account.analytic.line', 'task_id', 'Feuilles de temps',
                                           domain=[('is_timesheet', '=', True)])
    completion_rate = fields.Float(compute='get_progress', store=True, string=u"Taux d'achèvement", group_operator="avg")
    left_hours = fields.Float(compute='get_progress', store=True, string=u'Heures restantes')
    spent_hours = fields.Float(compute='get_progress', store=True, string=u'Heures passées')

    uom_id = fields.Many2one("uom.uom", string=u"UdM")

    end_date_state = fields.Selection([
        ('green', 'Green'),
        ('orange', 'Orange'),
        ('red', 'Red'),
    ], compute='_get_end_date_state', string='État de la date de fin')

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.date_start = fields.Date.today()

    @api.depends('date_start', 'date_deadline', 'completion_rate')
    def _get_end_date_state(self):
        for rec in self:
            date_from = fields.Datetime.from_string(rec.date_start)
            date_to = fields.Datetime.from_string(rec.date_deadline)
            current_date = fields.Datetime.from_string(fields.Datetime.now())
            if rec.completion_rate != 100 and date_to and date_from:
                expected_duration = (date_to - date_from).days
                current_duration = (current_date - date_from).days
                duration_pourcentage = ((float(current_duration) - expected_duration) / (expected_duration or 1)) * 100
                if duration_pourcentage > 20.0:
                    rec.end_date_state = 'red'
                elif duration_pourcentage > 10.0:
                    rec.end_date_state = 'orange'
                else:
                    rec.end_date_state = 'green'
            else:
                rec.end_date_state = 'green'

    @api.depends('timesheet_ids.unit_amount', 'planned_hours')
    def get_progress(self):
        for task in self.sorted(key='id', reverse=True):
            effective_hours = sum(task.timesheet_ids.filtered(lambda r: r.is_timesheet).mapped('unit_amount'))
            task.left_hours = task.planned_hours - effective_hours
            task.spent_hours = effective_hours
            task.completion_rate = round(100.0 * (effective_hours) / (task.planned_hours or 1.0), 2)


    @api.depends('timesheet_ids', 'timesheet_ids.amount')
    def get_cost_budget(self):
        for record in self:
            record.cost = sum([line.amount for line in record.timesheet_ids.filtered(lambda r: r.type == 'a')])
            record.budget = sum([line.amount for line in record.timesheet_ids.filtered(lambda r: r.type == 'f')])


    @api.depends('timesheet_ids')
    def get_actual_budget_count(self):
        for record in self:
            record.actual_count = len(record.timesheet_ids.filtered(lambda r: r.type == 'a'))
            record.budget_count = len(record.timesheet_ids.filtered(lambda r: r.type == 'f'))



    def get_budget_task_view(self):
        self.ensure_one()
        budget_ids = [line.id for line in self.timesheet_ids.filtered(lambda r: r.type == 'f')]
        return {
            'name': 'Budget',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'view_mode': 'tree,form,graph,pivot',
            'domain': [("id", "in", budget_ids), ('type', '=', 'f')],
            'context': {'type': 'f', 'default_type': 'f', 'default_project_id': self.project_id.id,
                        'default_task_id': self.id, 'default_account_id': self.project_id.analytic_account_id.id},
            'target': 'current',
        }


    def get_cost_task_view(self):
        self.ensure_one()
        budget_ids = [line.id for line in self.timesheet_ids.filtered(lambda r: r.type == 'a')]
        return {
            'name': 'Cost',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'view_mode': 'tree,form,graph',
            'domain': [("id", "in", budget_ids), ('type', '=', 'a')],
            'context': {'type': 'a', 'default_type': 'a', 'default_project_id': self.project_id.id,
                        'default_task_id': self.id, 'default_account_id': self.project_id.analytic_account_id.id},
            'target': 'current',
        }


    def copy(self, default):
        new_id = super(Task, self).copy(default)
        for timesheet in self.timesheet_ids.filtered(lambda t: t.type in (False, 'f')):
            new = timesheet.copy({'task_id': new_id.id,
                                  'project_id': new_id.project_id.id,
                                  })
            new.write({'type': timesheet.type})
        return new_id

    @api.constrains('date_start', 'date_deadline')
    def _check_dates(self):
        for record in self:
            if record.wbs_id and record.wbs_id.start_date and record.wbs_id.finish_date:
                if record.date_start and (record.date_start < record.wbs_id.start_date or record.date_start > record.wbs_id.finish_date):
                    raise ValidationError(
                    u'Date début de la tâche %s doit être entre date début et fin du wbs' % record.name)
                    # u'Task Start date should between WBS start and finish dates for task %s' % record.name)
                if record.date_deadline and (record.date_deadline < record.wbs_id.start_date or record.date_deadline > record.wbs_id.finish_date):
                    raise ValidationError(u'Date fin de la tâche %s doit être entre date début et fin du wbs  '%record.name)
                    # raise ValidationError(u'Task End date should between WBS start and finish dates for task %s'%record.name)

