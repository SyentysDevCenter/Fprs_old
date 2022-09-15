# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from collections import defaultdict


class SaleDpgfReport(models.AbstractModel):
	_name = 'report.project_sale_dpgf.report_saleorder_dpgf'

	def get_line_total(self, line):
		if line:
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


	def _get_report_values(self, docids, data = None):
		sales = self.env['sale.order'].browse(docids)
		if any(not l.dpgf_sale or l.dpgf_principal != 'principal' for l in sales):
			raise ValidationError('Tous les devis doivent être des devis de réabilitation principaux!')
		# order_lines = {}
		# for order in sales:
		# 	order_lines[order.id] = []
		# 	lines_amounts = defaultdict(lambda: {'line': self.env['sale.order'], 'subtotal': 0.0, 'total': 0.0})
		# 	for line in order.order_line:


		return {
			'doc_ids'  : docids,
			'doc_model': self.env['sale.order'],
			'data'     : data,
			'docs'     : sales,
			'get_line_total': self.get_line_total
		}