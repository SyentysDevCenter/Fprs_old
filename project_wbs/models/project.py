# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from datetime import datetime, timedelta


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'mail.thread', 'portal.mixin', 'mail.activity.mixin']


    wbs_ids = fields.One2many('project.wbs', 'project_id', 'WBS')
    wbs_count = fields.Integer(compute="get_wbs_count", string=u"# WBS", store=True)
    budget_count = fields.Float(u"Budget", compute="get_budget_count")
    cost_count = fields.Float(u"Coût", compute="get_cost_count")
    cost = fields.Float(u"Coût", compute="get_cost")
    budget = fields.Float(u"Budget", compute="get_budget")


    def get_cost(self):
        for record in self:
            wbs_ids = record.wbs_ids.filtered(lambda r: not r.parent_id)
            record.cost = sum([wbs.cost for wbs in wbs_ids])

    def action_open_gantt(self):
        self.ensure_one()
        wbs_ids = []
        for wbs in self.wbs_ids:
            wbs_ids.append(wbs.id)
        return {
            'name': 'Gantt chart',
            'type': 'ir.actions.act_window',
            'res_model': 'project.wbs',
            'view_mode': 'gantt',
            'target': 'current',
            'context': {'default_project_id': self.id, 'project_id': self.id},
            'domain': [("id", "in", wbs_ids)],
        }

    def get_cost_count(self):
        for record in self:
            wbs_ids = record.wbs_ids.filtered(lambda r: not r.parent_id)
            record.cost_count = sum([wbs.cost for wbs in wbs_ids])


    @api.depends('wbs_ids')
    def get_wbs_count(self):
        for record in self:
            record.wbs_count = len(record.wbs_ids)


    def get_budget(self):
        for record in self:
            wbs_ids = record.wbs_ids.filtered(lambda r: not r.parent_id)
            record.budget = sum([wbs.budget for wbs in wbs_ids])


    def get_budget_count(self):
        for record in self:
            wbs_ids = record.wbs_ids.filtered(lambda r: not r.parent_id)
            record.budget_count = sum([wbs.budget for wbs in wbs_ids])


    def get_wbs_tree_view(self):
        self.ensure_one()
        wbs_ids = [wbs.id for wbs in self.wbs_ids]
        return {
            'name': 'WBS',
            'type': 'ir.actions.act_window',
            'res_model': 'project.wbs',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("id", "in", wbs_ids)],
            'context': {'default_project_id': self.id},
            'target': 'current',
        }


    def get_budget_project_view(self):
        self.ensure_one()
        tree_view = self.env.ref('analytic.view_account_analytic_line_tree')
        form_view = self.env.ref('analytic.view_account_analytic_line_form')
        pivot_view = self.env.ref('analytic.view_account_analytic_line_pivot')
        budget_ids = []
        for wbs in self.wbs_ids:
            budgets = [budget.id for budget in wbs.budget_ids]
            budget_ids += budgets
        return {
            'name': 'Forecast',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form'), (pivot_view.id, 'pivot')],
            'view_mode': 'tree,form',
            'domain': [("id", "in", budget_ids), ('type', '=', 'f')],
            'context': {'type': 'f', 'default_type': 'f', 'default_account_id': self.analytic_account_id.id},
            'target': 'current',
        }


    def get_cost_project_view(self):
        tree_view = self.env.ref('analytic.view_account_analytic_line_tree')
        form_view = self.env.ref('analytic.view_account_analytic_line_form')
        pivot_view = self.env.ref('analytic.view_account_analytic_line_pivot')
        self.ensure_one()
        cost_ids = []
        for wbs in self.wbs_ids:
            costs = [cost.id for cost in wbs.cost_ids]
            cost_ids += costs
        return {
            'name': 'Cost',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form'), (pivot_view.id, 'pivot')],
            'domain': [("id", "in", cost_ids), ('type', '=', 'a')],
            'context': {'type': 'a', 'default_type': 'a', 'default_account_id': self.analytic_account_id.id},
            'target': 'current',
        }

