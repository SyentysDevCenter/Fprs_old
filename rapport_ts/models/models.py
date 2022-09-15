# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    matricule = fields.Char(string='Matricule')


class ProjectProject(models.Model):
    _inherit = 'project.project'



    @api.model_create_multi
    def create(self, vals):
        res = super(ProjectProject, self).create(vals)
        absence_task_vals = {}
        intemperie_vals = {}
        for rec in res:
            absence_task_vals['name'] = 'Absence'
            absence_task_vals['absence'] = True
            absence_task_vals['project_id'] = rec.id
            intemperie_vals['name'] = 'Intempérie'
            intemperie_vals['intemperie'] = True
            intemperie_vals['project_id'] = rec.id
            create_absence_task = self.env['project.task'].sudo().create(absence_task_vals)
            create_intemperie_task = self.env['project.task'].sudo().create(intemperie_vals)

        return res

class ProjectTask(models.Model):
    _inherit = 'project.task'

    absence = fields.Boolean(string='Absence ?')
    intemperie = fields.Boolean(string='Intempérie ?')

    @api.constrains('absence', 'intemperie')
    def checks(self):
        for rec in self:
            if rec.absence and rec.intemperie:
                raise ValidationError('Une tâche ne peut pas être à la fois Absence et Intempérie !')

    def unlink(self):
        for rec in self:
            if rec.absence or rec.intemperie:
                raise ValidationError('Vous ne pouvez pas supprimer une tâche Absence / Intempérie !')
        return super(ProjectTask, self).unlink()


    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        for record in self:
            if res and record.project_id:
                if vals.get('absence', False):
                    if any(l.absence for l in record.project_id.task_ids.filtered(lambda u: u.id != record.id)):
                        raise ValidationError(
                        u'Il existe déjà une tâche Absence pour le projet %s' % record.project_id.name)

                if vals.get('intemperie', False):
                    if any(l.intemperie for l in record.project_id.task_ids.filtered(lambda u: u.id != record.id)):
                        raise ValidationError(
                        u'Il existe déjà une tâche Intempérie pour le projet %s' % record.project_id.name)

        return res

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        if res and res.project_id:
            if vals.get('absence'):
                project = self.env['project.project'].browse(res.project_id.id)
                if project and project.task_ids:
                    if any(rec.absence for rec in project.task_ids.filtered(lambda u: u.id != res.id)):
                        raise ValidationError(
                            u'Il existe déjà une tâche Absence pour le projet %s'  % project.name)

            if vals.get('intemperie'):
                project = self.env['project.project'].browse(res.project_id.id)
                if project and project.task_ids:
                    if any(rec.intemperie for rec in project.task_ids.filtered(lambda u: u.id != res.id)):
                            raise ValidationError(
                                u'Il existe déjà une tâche Intempérie pour le projet %s'  % project.name)
        return res




class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    absence = fields.Boolean(related='task_id.absence', store=True)
    intemperie = fields.Boolean(related='task_id.intemperie', store=True)


