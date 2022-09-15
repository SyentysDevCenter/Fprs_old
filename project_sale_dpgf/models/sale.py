# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	dpgf_sale = fields.Boolean('Devis réabilitation')
	affaire = fields.Text(string='Affaire')
	is_dpgf_principal = fields.Boolean("Devis réabilitation principal")
	dpgf_state = fields.Selection([('progress', 'En cours'), ('accepte', 'Accepté'), ('refuse', 'Refusé')],
								  default='progress', string='Etat du devis de réabilitation')

	@api.model
	def create(self, vals):


		if vals.get('dpgf_sale', False) and vals['dpgf_sale']:
			vals['name'] = self.env['ir.sequence'].next_by_code('sale.dpgf.seq')

		res = super(SaleOrder, self).create(vals)

		return res

	@api.constrains('chantier_id','dpgf_sale', 'is_dpgf_principal')
	def check_chantier_dpgf(self):
		for rec in self:
			if rec.dpgf_sale and not rec.chantier_id:
				raise ValidationError("Le devis de réabilitation doit être lié à un chantier!")
			if rec.is_dpgf_principal and rec.dpgf_sale and rec.chantier_id:
				others = self.env['sale.order'].search_count([('is_dpgf_principal', '=', 'True'),
														('dpgf_sale', '=', True),
														('chantier_id', '=', rec.chantier_id.id),
														])
				if others >1:
					raise ValidationError("Un chantier ne peut avoir qu'un seul devis de réabilitation principal!")


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	wbs_id = fields.Many2one('project.wbs', 'Ligne de DPGF')
	code_client = fields.Char("Code Client")

	def get_line_total(self):
		self.ensure_one
		line = self
		if not line.display_type:
			subtotal = line.price_subtotal
			total = line.price_total
		elif line.display_type == 'line_section':
			childs = self.env['project.wbs'].search([('id', 'child_of', line.wbs_id.id),

													 ('is_invoicable', '=', True),
													 ('product_id', '!=', False),
													 ])
			if childs and childs.mapped('sale_line_ids'):
				subtotal = sum(l.price_subtotal for l in childs.mapped('sale_line_ids').filtered(lambda r: r.order_id == line.order_id))
				total = sum(l.price_total for l in childs.mapped('sale_line_ids').filtered(lambda r: r.order_id == line.order_id))
			else:
				subtotal = 0.0
				total = 0.0
		else:
			subtotal = 0.0
			total = 0.0
		return subtotal, total

class ProjectWbs(models.Model):
	_inherit = 'project.wbs'

	sale_line_ids = fields.One2many('sale.order.line', 'wbs_id')

	@api.model
	def create(self, vals):
		if vals.get('project_id', False):
			project = self.env['project.project'].browse(vals['project_id'])
			if project and project.has_dpgf_principal:
				raise ValidationError('Vous ne pouvez pas créer une ligne WBS pour un projet ayant un devis'
									  ' de réabilitation pricipal créé!')
		res = super(ProjectWbs, self).create(vals)
		return res

	def write(self, vals):
		if vals.get('product_id', False) or vals.get('qty', False) or vals.get('unit_price', False) or \
				vals.get('name', False) or vals.get('code', False)  or vals.get('project_id', False)\
				or 'is_invoicable' in vals :
			for rec in self:
				if rec.sale_line_ids:
					raise ValidationError('Vous ne pouvez pas modifier une ligne WBS ayant un ligne de devis'
									  ' créée!')
		res = super(ProjectWbs, self).write(vals)
		return res

	@api.constrains('sale_line_ids', 'product_id')
	def check_product_id(self):
		for rec in self:
			if rec.sale_line_ids and rec.product_id:
				if rec.product_id not in rec.sale_line_ids.mapped('product_id'):
					raise ValidationError("Vous ne pouvez pas changer l'article de facturation d'une ligne liée à une ligne de vente")