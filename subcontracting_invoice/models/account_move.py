# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
	_inherit = 'account.move'


	sous_traitant_id = fields.Many2one('res.partner', domain="[('sous_traitant', '=', True)]")
	subcontracting_refund_id =  fields.Many2one('account.move', 'Avoir de sous-traitance')
	origin_invoice_ids = fields.One2many('account.move', 'subcontracting_refund_id', "Facture d'origine")
	subcontracting_refund = fields.Boolean()
	sous_traitant = fields.Boolean('partenaire sous-traitant', related = 'partner_id.sous_traitant', store = True)
	soustraitant = fields.Boolean('Facture de sous-traitant')

	def generate_subcontracting_refund(self):
		pass

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	origin_invoice_line_id = fields.Many2one('account.move.line')

class ResCompany(models.Model):
	_inherit = 'res.company'

	subcontracting_marge = fields.Float('Marge de soutraitance')
	subcontract_product_id = fields.Many2one('product.product')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    sous_traitant = fields.Boolean('Sous traitant', related='partner_id.sous_traitant', store=True)
