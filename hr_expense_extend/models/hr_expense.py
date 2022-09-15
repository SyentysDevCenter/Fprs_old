# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrExpenseSheet(models.Model):
	_inherit = 'hr.expense.sheet'

	remboursement_espece = fields.Boolean('Remboursement en espèce')
	remboursement_virement = fields.Boolean('Remboursement par virement')