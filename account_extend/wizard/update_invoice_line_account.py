# -*- coding: utf-8 -*-


from odoo import api, fields, models


class UpdateInvoiceLineAccount(models.TransientModel):
	_name = 'update.invoice.line.account'

	new_account_id = fields.Many2one('account.account', 'Compte à utiliser')
	old_account_id = fields.Many2one('account.account', 'Compte actuel', related='invoice_line_id.account_id')
	invoice_line_id = fields.Many2one('account.move.line', 'Ligne')

	@api.model
	def default_get(self, default_fields):
		# OVERRIDE
		values = super(UpdateInvoiceLineAccount, self).default_get(default_fields)
		invoice_line_id = self._context.get('active_id', False)
		values.update({'invoice_line_id': invoice_line_id})
		return values

	def update_account(self):
		self.invoice_line_id.write({'account_id': self.new_account_id.id})