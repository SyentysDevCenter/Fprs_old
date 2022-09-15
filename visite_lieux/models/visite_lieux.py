# -*- coding: utf-8 -*-

from odoo import api, models, fields


class VisiteLieu(models.Model):
    _name = 'visite.lieu'
    _rec_name = 'objet_visite'

    objet_visite = fields.Char(string="Objet de la visite", required=True)
    type = fields.Selection([('individuelle', 'Individuelle'),
                             ('collective', 'Collective')],
                            default='individuelle')
    lieu_visite = fields.Char(string="Lieu", required=True)
    date_visite = fields.Date(string="Date")
    user_id = fields.Many2one('res.partner', 'Responsable')
    nature_terrain = fields.Many2one("visite.terrain",
                                     string='Nature du terrain',
                                     required=False)
    evacuation_deblai = fields.Boolean(string="Evacuation du déblai")
    deblai_utilisable = fields.Boolean(string="Déblai utilisable")
    distance = fields.Integer(string="Distance carrière (km)")
    provenance_materiaux = fields.Integer(string="Provenance des matériaux (distance carrière")
    raccordement_eau = fields.Boolean(string="Raccordement (Eau potable)")
    raccordement_elec = fields.Boolean(string="Raccordement (Electricité)")
    acces_terrain = fields.Selection([('f', 'Facile'),
                                      ('m', 'moyen'),
                                      ('d', 'difficile')],
                                     default='m', string="Accès terrain")
    observations = fields.Text(string="Observations")
    compte_rendu = fields.Binary('Compte rendu')
    state = fields.Selection([('nouveau', 'Nouveau'), ('done', u'Effectuée'), ('cancel', 'Annulée')], default='nouveau')


    @api.depends('objet_visite')
    def _compute_visite_name(self):
        for rec in self:
            rec.name = rec.objet_visite

    def to_effectue(self):
        self.write({
            'state': 'done'
        })

    def to_annule(self):
        self.write({
            'state': 'cancel'
        })


class NatureTerrain(models.Model):
    _name = "visite.terrain"

    name = fields.Char('Nature de terrain')