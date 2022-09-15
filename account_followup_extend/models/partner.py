# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
	_inherit = 'res.partner'

	def consult_account_move_line(self):
		print('dddddd', self)
		vals = {
			'view_id'     : self.env.ref('account_followup_extend.view_move_line_tree_specific').id,
			'user_type_id': self.env.ref('account.data_account_type_receivable').id
		}

		return vals