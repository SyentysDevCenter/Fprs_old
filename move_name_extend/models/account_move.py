# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountJournal(models.Model):
	_inherit = 'account.journal'

	refund_code = fields.Char('Code des avoirs')

class AccountMove(models.Model):
	_inherit = 'account.move'

	name = fields.Char(default='/')

	def _get_starting_sequence(self):
		starting_sequence = super()._get_starting_sequence()
		if self.journal_id.refund_sequence and self.move_type in ('out_refund', 'in_refund') and starting_sequence and starting_sequence.split('/', maxsplit=1)[0]=='R'+self.journal_id.code and self.journal_id.refund_code:
			starting_sequence = self.journal_id.refund_code+'/' + starting_sequence.split('/', maxsplit=1)[1]
		return starting_sequence

	@api.depends('posted_before', 'state', 'journal_id', 'date')
	def _compute_name(self):
		res = super()._compute_name()
		for move in self:
			if move.name != '/' and move == self[0] and not move.posted_before and move.date and move.state == 'draft':
				move.name = '/'

