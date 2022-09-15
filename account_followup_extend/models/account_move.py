# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	user_type_id = fields.Many2one(related = 'account_id.user_type_id', store = True)

	def inclure_action(self):
		active_ids = self._context.get('active_ids', [])
		account_move_lines = self.env['account.move.line'].sudo().browse(active_ids)
		if account_move_lines:
			account_move_lines.write({'blocked': False})

	def exclure_action(self):
		active_ids = self._context.get('active_ids', [])
		account_move_lines = self.env['account.move.line'].sudo().browse(active_ids)
		if account_move_lines:
			account_move_lines.write({'blocked': True})