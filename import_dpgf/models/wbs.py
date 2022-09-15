# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SDP(models.Model):
    _inherit = 'wbs.cost.line'

    uom_id = fields.Many2one('uom.uom', string='UdM')
