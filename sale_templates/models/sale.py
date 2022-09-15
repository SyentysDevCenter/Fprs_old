# -*- coding: utf-8 -*-

from odoo import api, fields, models
import locale
import datetime

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	attention_de = fields.Char("A l'attention de")
	titre = fields.Char('Titre')
	formated_date = fields.Char(compute='compute_formated_date', store=True)
	devis_text_1 = fields.Html('Texte devis régul', default=lambda self: self.env.user.company_id.devis_text_1)
	devis_text_2 = fields.Html('Texte du devis 2', default=lambda self: self.env.user.company_id.devis_text_2)
	framed_text = fields.Html('Texte Encadré')
	partner_address_1 =fields.Char("Adresse locataire/particulier")

	nom_client_final = fields.Char('Nom/prénom')
	appart_client_final = fields.Char('N° appartement')
	ville_client_final = fields.Char('Ville')
	tel_client_final = fields.Char('Tél')
	code_postal = fields.Char('Code postal')
	civility = fields.Many2one('res.partner.title', 'Civilité client final')
	text_civility = fields.Many2one('res.partner.title', 'Civilité texte')
	text_debut = fields.Char(default='Bonjour ')

	@api.depends('date_order')
	def compute_formated_date(self):
		for rec in self:

			locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
			rec.formated_date = datetime.datetime.strftime(rec.date_order, '%B %Y').upper()


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	def get_sale_order_line_multiline_description_sale(self, product):
		""" Compute a default multiline description for this sales order line.

		In most cases the product description is enough but sometimes we need to append information that only
		exists on the sale order line itself.
		e.g:
		- custom attributes and attributes that don't create variants, both introduced by the "product configurator"
		- in event_sale we need to know specifically the sales order line as well as the product to generate the name:
		  the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
		"""
		res = super(SaleOrderLine, self).get_sale_order_line_multiline_description_sale(product)
		if product.description_sale:
			res = product.description_sale +  self._get_sale_order_line_multiline_description_variants()
		return res