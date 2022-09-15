# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AoEvaluation(models.Model):
    _name = 'ao.evaluation'

    element_id = fields.Many2one('ao.evaluation.element', u'Élément d’évaluation')
    critere = fields.Char(u'Critères de similarité')
    operateur = fields.Selection([('<', '<'), ('=', '='), ('>', '>'), ('>=', '>='), ('<=', '<=')], u'Opérateur')
    reference = fields.Float(u'Nombre de référence')
    unite = fields.Char(u'Unité')
    ao_id = fields.Many2one('ao.ao', "Appel d'offre")

class AoEvaluationElement(models.Model):
    _name = 'ao.evaluation.element'

    name = fields.Char('Element', required=True)

