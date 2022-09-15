# -*- coding: utf-8 -*-

from odoo import api, fields, models



class SuiviEmetteurBc(models.Model):
    _name = 'suivi.emetteur.bc'
    _description = 'Suivi Emetteur BC'

    name = fields.Char(string='Nom')


