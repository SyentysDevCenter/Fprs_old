# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AoAdmission(models.Model):
    _name = 'ao.admission'

    name = fields.Char(string='Description', required=False)
    element_id = fields.Many2one('ao.admission.element', u'Élément d’admission')
    critere = fields.Char(u'Critères de similarité')
    operateur = fields.Selection([('<', '<'), ('=', '='), ('>', '>'), ('>=', '>='), ('<=', '<=')], u'Opérateur')
    reference = fields.Float(u'Nombre de référence')
    unite = fields.Char(u'Unité')
    ao_id = fields.Many2one('ao.ao', "Appel d'offre")
    type = fields.Many2one('ao.admission.type', 'Type')


class AoAdmissionType(models.Model):
    _name = 'ao.admission.type'

    name = fields.Char(required=True)


class AoAdmissionElement(models.Model):
    _name = 'ao.admission.element'

    name = fields.Char('Element', required=True)
    type = fields.Many2one('ao.admission.type', 'Type')
