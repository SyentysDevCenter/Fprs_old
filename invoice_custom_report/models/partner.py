# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_report_model_id = fields.Many2one('ir.actions.report', string="Modèle d'impression", domain="[('model','=','account.move')]")
    sale_report_model_id = fields.Many2one('ir.actions.report', string="Modèle d'impression", domain="[('model','=','sale.order')]")
