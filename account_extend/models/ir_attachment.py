# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import UserError




class IrAttachement(models.Model):
    _inherit = 'ir.attachment'

    sale_attachement_id = fields.Many2one('ir.attachment')

