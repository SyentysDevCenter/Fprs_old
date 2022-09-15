# -*- coding: utf-8 -*-
from odoo import api, fields, models


class JugementAdministratif(models.Model):
    _name = "ao.jugement.administratif"
    _description = "Jugement administratif des AO"

    name = fields.Char(string=u"Complément de dossier", required=True)
    date_notif = fields.Date(string="Date notification")
    date_limite = fields.Date(string="Date limite")
    date_depot = fields.Date(string=u"Date dépôt")
    ao_id = fields.Many2one('ao.ao', 'AO', ondelete='cascade')


class JugementTechnique(models.Model):
    _name = "ao.jugement.technique"
    _description = "Jugement technique des AO"

    name = fields.Char(string=u"Complément de dossier", required=True)
    date_notif = fields.Date(string="Date notification")
    date_limite = fields.Date(string="Date limite")
    date_depot = fields.Date(string=u"Date dépôt")
    ao_id = fields.Many2one('ao.ao', 'AO', ondelete='cascade')


class AoJugementLine(models.Model):
    _name = "ao.jugement.line"
    _description = "Jugement financier des AO"
    _order = "montant"

    @api.onchange("ecarte")
    def _ecarte(self):
        if self.ecarte:
            self.montant = 0.0
            self.classement = 0.0

    @api.depends("ao_id", "montant")
    def _compute_ecart(self):
        for rec in self:
            if rec.ecarte:
                rec.ecart_pourcent = 0.0
                rec.ecart = 0.0
            else:
                if rec.ao_id.montant_soumission:
                    rec.ecart = rec.montant - rec.ao_id.montant_soumission
                    rec.ecart_pourcent = (rec.ecart / rec.ao_id.montant_soumission) * 100
                else:
                    rec.ecart = 0.0
                    rec.ecart_pourcent = 0.0

    concurrent = fields.Many2one('ao.concurent', "Concurrent", required=True)
    montant = fields.Float()
    ecarte = fields.Boolean(u"Ecarté")
    classement = fields.Integer(readonly=True)
    ecart = fields.Float("Ecart", compute="_compute_ecart")
    ecart_pourcent = fields.Float(u"Ecart(%)", compute="_compute_ecart")
    observation = fields.Char()
    ao_id = fields.Many2one('ao.ao', "AO", ondelete='cascade')

    _sql_constraints = [
        ('concurrent_ao_id',
         'unique(concurrent,ao_id)',
         u'le concurrent doit être unique!')
    ]


class AoConcurrent(models.Model):
    _name = "ao.concurent"
    _description = "Concurrent"

    name = fields.Char("Concurrent", required=True)


class MotifRejet(models.Model):
    _name = "ao.motif.rejet"
    _description = "Motif de rejet AO"

    name = fields.Char("Motif de rejet", required=True)
