# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AoRisk(models.Model):
    _name = 'ao.risk'

    name = fields.Char('Description', required=True)
    ao_id = fields.Many2one('ao.ao', 'AO')
    date = fields.Date()
    niveau = fields.Selection([('high', u'Elevé'),
                               ('medium', 'Moyen'),
                               ('low', 'Faible')], 'Niveau', default='medium')
    user_id = fields.Many2one('res.users', 'Responsable')
    control_measure = fields.Text(u'Mesure de contrôle')
    type = fields.Selection([('ao', 'Ao'), ('projet', 'Projet'), ('autre', 'Autres')], default='ao')
    state = fields.Selection([('new', u'Nouveau'),
                              ('en_cours', 'En cours'),
                              ('traite', 'Traité')], string='Etat')