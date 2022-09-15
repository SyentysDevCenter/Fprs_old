# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectProject(models.Model):
	_inherit = 'project.project'

	product_pricelist_id = fields.Many2one('product.pricelist', string='Liste de prix')


