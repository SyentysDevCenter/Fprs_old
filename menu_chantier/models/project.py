# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_rehabilitation = fields.Boolean('Réhabilitation')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_rehabilitation = fields.Boolean('Réhabilitation', related='project_id.is_rehabilitation', store=True)
