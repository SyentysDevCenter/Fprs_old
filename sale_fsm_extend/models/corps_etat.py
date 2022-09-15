# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CorpsEtat(models.Model):
    _name = 'corps.etat'

    name = fields.Char("Nom", required=True)
