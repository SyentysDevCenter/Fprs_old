# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError



class ProjectEtat(models.Model):
    _name = 'project.etat'
    _description = "Etat de projet"

    name = fields.Char(string='Nom', required=True)
