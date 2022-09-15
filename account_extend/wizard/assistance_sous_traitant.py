# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssistantSousTraitance(models.TransientModel):
    _name = 'assistant.sous.traitance'

    line_ids = fields.One2many('assistant.sous.traitance.line', 'wizard_id')
    active_invoice_line_ids = fields.Many2many('account.move.line')

    def apply_sous_traitance(self):
        if not self.line_ids:
            raise ValidationError('Veuillez ajouter des lignes de factures !')
        else:
            invoices = self.line_ids.mapped('move_id')
            for line in self.line_ids:
                line.move_line_id.write({'sous_traitance': line.sous_traitance})

            action = self.env.ref('gecop_model_reports.gecop_invoice_sous_traitant_report_id').report_action(
                invoices, data={})
            action.update({'close_on_report_download': True})

            return action



class AssistantSousTritantLine(models.TransientModel):
    _name = 'assistant.sous.traitance.line'

    wizard_id = fields.Many2one('assistant.sous.traitance')
    move_line_id = fields.Many2one('account.move.line', string='Ligne de facture')
    move_id = fields.Many2one(related='move_line_id.move_id', string='Facture associée')
    product_id = fields.Many2one(related='move_line_id.product_id' ,string='Produit')
    qty = fields.Float(related='move_line_id.quantity', string='Qty')
    price = fields.Float(related='move_line_id.price_unit', string='Prix')
    currency_id = fields.Many2one(related='move_line_id.currency_id')
    sous_traitance = fields.Boolean(string='Sous Traitance')
