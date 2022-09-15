# -*- coding: utf-8 -*-

from odoo import fields, api, models
from odoo.exceptions import ValidationError


class AO(models.Model):
    _inherit = 'ao.ao'

    project_id = fields.Many2one('project.project', u"Projet")
    project_active = fields.Boolean(u'Project active', compute="is_project_active")
    budget = fields.Float(u"Forecast", compute="get_budget")


    def get_budget(self):
        for record in self:
            budget = 0
            if record.project_id:
                wbs_ids = record.project_id.wbs_ids.filtered(lambda r: not r.parent_id)
                budget = sum([wbs.budget for wbs in wbs_ids])
            record.budget = budget


    def is_project_active(self):
        for record in self:
            record.project_active = record.project_id.active


    def button_gagne(self):
        res = super(AO, self).button_gagne()
        for rec in self:
            if not rec.project_id:
                raise ValidationError(u"Merci de créer le BDP avant de passer à l'état gagné")
            rec.project_id.active = True
            rec.project_id.partner_id = rec.partner_id
            rec.project_id.condition_facturation = rec.condition_facturation
        return True


    def action_open_project(self):
        self.ensure_one()
        if not self.project_id:
            project_obj = self.env['project.project']
            project_id = project_obj.create(
                {
                    'name': self.name,
                }
            )
            self.project_id = project_id
        action = {
                'name': 'Project',
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'view_type': 'form',
                'view_mode': 'form',
                # 'context': {'default_ao_id': self.id},
                'res_id': self.project_id.id,
                'target': 'current',
        }
        return action


    def action_open_project_wbs(self):
        self.ensure_one()
        if not self.project_id:
            project_obj = self.env['project.project']
            project_id = project_obj.create(
                {
                    'name': self.name,
                    'active': False,
                }
            )
            self.project_id = project_id
        wbs_ids = [wbs.id for wbs in self.project_id.wbs_ids]
        action ={
            'name': 'BdP',
            'type': 'ir.actions.act_window',
            'res_model': 'project.wbs',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("id", "in", wbs_ids)],
            'context': {'default_project_id': self.project_id.id},
            'target': 'current',
        }
        return action


    def action_open_gantt(self):
        self.ensure_one()
        wbs_ids = []
        for wbs in self.project_id.wbs_ids:
            wbs_ids.append(wbs.id)
        return {
            'name': 'Gantt chart',
            'type': 'ir.actions.act_window',
            'res_model': 'project.wbs',
            'view_mode': 'gantt_view',
            'target': 'current',
            'context': {'default_project_id': self.project_id.id, 'project_id': self.project_id.id},
            'domain': [("id", "in", wbs_ids)],
        }


    def get_budget_ao_view(self):
        self.ensure_one()
        tree_view = self.env.ref('analytic.view_account_analytic_line_tree')
        form_view = self.env.ref('analytic.view_account_analytic_line_form')
        pivot_view = self.env.ref('analytic.view_account_analytic_line_pivot')
        budget_ids = []
        account_id = False
        if self.project_id:
            account_id = self.project_id.analytic_account_id.id
            for wbs in self.project_id.wbs_ids:
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
            'context': {'type': 'f', 'default_type': 'f', 'default_account_id': account_id},
            'target': 'current',
        }

class Project(models.Model):
    _inherit = 'project.project'

    condition_facturation = fields.Text('Condition de facturation')

