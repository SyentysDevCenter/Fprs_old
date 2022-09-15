# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	generic = fields.Boolean('Article générique')
	contract_line_ids = fields.One2many('sale.contract.line', 'product_id')


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	active_contract = fields.Many2one('sale.contract','Contrat actif', compute='compute_actif_contract', store=True)
	pricelist_product_ids = fields.Many2many('product.product', compute = 'compute_pricelist_products', store = True)


	@api.depends('partner_id', 'pricelist_id')
	def compute_pricelist_products(self):
		sale_products = self.env['product.product'].search([('sale_ok', '=', True)])
		for r in self:

			if r.pricelist_id:
				order_pricelist = r.pricelist_id
				if order_pricelist.item_ids:
					var_lines = order_pricelist.item_ids.filtered(
						lambda u: u.applied_on in ['0_product_variant', '1_product'])
					if var_lines:
						products = var_lines.mapped('product_id')
						products |= var_lines.mapped('product_tmpl_id.product_variant_id')
						if products:
							r.pricelist_product_ids = [(6,0,products.mapped('id'))]

	@api.onchange('partner_id')
	def onchange_partner_id(self):
		res = super().onchange_partner_id()
		if self.chantier_id and self.chantier_id.product_pricelist_id:
			self.update({'pricelist_id' : self.chantier_id.product_pricelist_id.id})


	def mettre_a_jour_prix(self):
		if self.chantier_id and self.chantier_id.product_pricelist_id:
			self.update({'pricelist_id': self.chantier_id.product_pricelist_id.id})
		elif self.partner_id:
			self.update({'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,})
		self.update_prices()


	@api.depends('partner_id', 'chantier_id')
	def compute_actif_contract(self):
		for rec in self:
			active_contract = False
			if rec.chantier_id:
				contract = self.env['sale.contract'].search([('chantier_id', '=', rec.chantier_id.id)])
				if contract:
					active_contract = contract

			elif (not rec.chantier_id or not active_contract) and rec.partner_id and rec.partner_id.contract_ids:
				active_contract = rec.partner_id.contract_ids.filtered(lambda r: r.date_start and r.date_start <=fields.Date.context_today(self) and
																					 (not r.date_end or r.date_end > fields.Date.context_today(self))
																	   and r.state == 'confirm')
				if active_contract:
					active_contract = active_contract[0].id
			rec.active_contract = active_contract

	@api.onchange('chantier_id')
	def onchange_chantier_id(self):
		super(SaleOrder, self).onchange_chantier_id()

		if self.chantier_id:
			if self.chantier_id.product_pricelist_id:
				self.update({'pricelist_id' : self.chantier_id.product_pricelist_id.id})





class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	active_contract = fields.Many2one(related='order_id.active_contract' , store=True)
	price_list_product_ids = fields.Many2many('product.product', compute='compute_pricelist_products', store=True)
	#
	#
	@api.depends('order_id', 'order_id.pricelist_id', 'active_contract')
	def compute_pricelist_products(self):
		sale_products = self.env['product.product'].search([('sale_ok', '=', True)])
		for r in self:
			if r.order_id:
				if r.order_id.pricelist_id:
					order_pricelist = r.order_id.pricelist_id
					if order_pricelist.item_ids:
						var_lines = order_pricelist.item_ids.filtered(lambda u: u.applied_on in ['0_product_variant', '1_product'])
						if var_lines:
							products = var_lines.mapped('product_id')
							products|=var_lines.mapped('product_tmpl_id.product_variant_id')
							if products:
								r.price_list_product_ids = products.ids
				# 		else:
				# 			r.price_list_product_ids = [(6, 0, sale_products.ids)]
				# 	else:
				# 		r.price_list_product_ids = [(6, 0, sale_products.ids)]
				# else:
				# 	r.price_list_product_ids = [(6, 0, sale_products.ids)]


	#
