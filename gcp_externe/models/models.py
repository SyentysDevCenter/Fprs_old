# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    corps_etat = fields.Char(string="CORPS D'ETAT")
    etat_chantier = fields.Selection([('etudes', 'ETUDES'),('travaux', 'TRAVAUX'),('acheve', 'ACHEVÉ'),('annule', 'ANNULÉ')], string='ETAT')



class ResCompany(models.Model):
    _inherit = 'res.company'

    entete = fields.Binary(string='Entête factures')

