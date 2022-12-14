# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_rehabilitation = fields.Boolean('RĂ©habilitation')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_rehabilitation = fields.Boolean('RĂ©habilitation', related='project_id.is_rehabilitation', store=True)
