# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Project(models.Model):
	_inherit = 'project.project'

	has_dpgf_principal = fields.Boolean('DPGF principal créé', compute='compute_has_dpgf_principal', store=True)

	@api.depends('chantier_sale_ids', 'chantier_sale_ids.is_dpgf_principal', 'chantier_sale_ids.dpgf_sale')
	def compute_has_dpgf_principal(self):
		for rec in self:
			if rec.chantier_sale_ids and any(l.dpgf_sale and l.is_dpgf_principal for l in rec.chantier_sale_ids):
				rec.has_dpgf_principal = True
			else:
				rec.has_dpgf_principal = False

	def project_create_sale(self):
		for rec in self:
			if not rec.partner_id:
				raise ValidationError('Vous ne pouvez pas créer un devis pour un chantier sans client!')
			sale_id = self.env['sale.order'].create({'partner_id' : rec.partner_id.id,
													 'date_order' : fields.Date.context_today(self),
													 'chantier_id'      : rec.id,
													 'dpgf_sale': True,
													 'is_dpgf_principal': True
													 })
			# for line in rec.wbs_ids.filtered(lambda r: r.is_invoicable):
			for line in rec.wbs_ids:
				if line.is_invoicable:
					if not line.product_id:
						raise ValidationError(
							'Aucun article de facturation trouvé pour la ligne %s!' % (line.name))
					else:
						product_to_use = line.product_id
					self.env['sale.order.line'].create({'product_id'     : product_to_use.id,
														'name'           : line.name,
														'code_client'           : line.code_client,
														'price_unit'     : line.unit_price,
														'product_uom_qty': line.qty,
														'product_uom'    : line.uom_id and line.uom_id.id or product_to_use.uom_id.id,
														'order_id'       : sale_id.id,
														'wbs_id'         : line.id
														})

				else:
					self.env['sale.order.line'].create({'display_type'     : 'line_section',
														'name'           : line.name,
														'order_id'       : sale_id.id,
														'wbs_id'         : line.id
														})

			return {"type"     : "ir.actions.act_window",
					"res_model": "sale.order",
					"domain"   : [("id", "=", sale_id.id)],
					"name"     : "Devis/Commande",
					"view_mode": 'tree,form'}
