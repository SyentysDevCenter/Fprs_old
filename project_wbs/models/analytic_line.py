# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def _get_account(self):
        if self.env.context.get('task_id'):
            task_id = self.env['project.task'].browse(self.env.context.get('task_id'))
            return task_id.project_id.analytic_account_id
        if self.env.context.get('project_id'):
            project_id = self.env['project.project'].browse(self.env.context.get('project_id'))
            return project_id.analytic_account_id

    wbs_id = fields.Many2one('project.wbs', 'WBS', ondelete='restrict', index=True)
    account_id = fields.Many2one('account.analytic.account', 'Code chantier', required=True, ondelete='restrict',
                                 index=True, default=_get_account)
    is_timesheet = fields.Boolean('Timesheet?')

    @api.model
    def create(self, vals):

        type = self.env.context.get('default_type', False)
        if (not type) or (type not in ('a', 'f')):
            vals['type'] = 'a'
        if vals.get('task_id', False):
            task_id = self.env['project.task'].browse(vals.get('task_id', False))
            vals['wbs_id'] = task_id.wbs_id.id
            vals['is_timesheet'] = True

        if self.env.context.get('task_id'):
            task_id = self.env['project.task'].browse(self.env.context.get('task_id'))
            vals['task_id'] = task_id.id
            vals['wbs_id'] = task_id.wbs_id.id
            vals['project_id'] = task_id.project_id.id
            vals['is_timesheet'] = True
        account_line_id = super(AccountAnalyticLine, self).create(vals)
        if account_line_id.task_id and account_line_id.is_timesheet and account_line_id.user_id:
            employee_id = self.env['hr.employee'].search([('user_id', '=', account_line_id.user_id.id)])
            if employee_id:
                account_line_id.amount = employee_id.cost_timesheet * account_line_id.unit_amount
        return account_line_id

    @api.onchange('task_id')
    def onchange_task(self):
        if self.task_id:
            self.wbs_id = self.task_id.wbs_id


    def write(self, vals):
        if vals.get('user_id', False) or vals.get('unit_amount', False):
             user_id = vals.get('user_id', False) or self.user_id.id
             unit_amount = vals.get('unit_amount', False) or self.unit_amount
             employee_id = self.env['hr.employee'].search([('user_id', '=', user_id)])
             if employee_id:
                 vals['amount'] = employee_id[0].cost_timesheet * unit_amount
        res = super(AccountAnalyticLine, self).write(vals)

        return res




