# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json


class AccountGeneralLedgerReport(models.AbstractModel):
	_inherit = "account.partner.ledger"

	def get_html(self, options, line_id = None, additional_context = None):
		if not options.get('unfold_all', False):
			ctx = self._context.copy()
			ctx['balance_ctx'] = True
			self = self.with_context(ctx)
		return super().get_html(options, line_id = line_id, additional_context=additional_context )

	def get_report_filename(self, options):
		"""The name that will be used for the file when downloading pdf,xlsx,..."""
		if not options.get('unfold_all', False):
			ctx = self._context.copy()
			ctx['balance_ctx'] = True
			self = self.with_context(ctx)
		return super().get_report_filename(options)

	@api.model
	def _get_report_name(self):
		name = super()._get_report_name()
		if 'balance_ctx' in self._context:
			name = 'Balance des tiers'
		else:
			name = 'Grand livre des tiers'
		return name

	@api.model
	def _get_partner_ledger_lines(self, options, line_id = None):
		''' Get lines for the whole report or for a specific line.
		:param options: The report options.
		:return:        A list of lines, each one represented by a dictionary.
		'''
		lines = []
		unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])
		if 'unfold_all_forced' in options:
			unfold_all = options['unfold_all_forced']
		expanded_partner = line_id and self.env['res.partner'].browse(int(line_id[8:]))
		partners_results = self._do_query(options, expanded_partner = expanded_partner)

		total_initial_balance = total_debit = total_credit = total_balance = 0.0
		for partner, results in partners_results:
			is_unfolded = 'partner_%s' % (partner.id if partner else 0) in options['unfolded_lines']

			# res.partner record line.
			partner_sum = results.get('sum', {})
			partner_init_bal = results.get('initial_balance', {})

			initial_balance = partner_init_bal.get('balance', 0.0)
			debit = partner_sum.get('debit', 0.0)
			credit = partner_sum.get('credit', 0.0)
			balance = initial_balance + partner_sum.get('balance', 0.0)

			lines.append(self._get_report_line_partner(options, partner, initial_balance, debit, credit, balance))

			total_initial_balance += initial_balance
			total_debit += debit
			total_credit += credit
			total_balance += balance

			if unfold_all or is_unfolded:
				cumulated_balance = initial_balance

				# account.move.line record lines.
				amls = results.get('lines', [])

				load_more_remaining = len(amls)
				load_more_counter = self._context.get('print_mode') and load_more_remaining or self.MAX_LINES

				for aml in amls:
					# Don't show more line than load_more_counter.
					if load_more_counter == 0:
						break

					cumulated_init_balance = cumulated_balance
					cumulated_balance += aml['balance']
					lines.append(self._get_report_line_move_line(options, partner, aml, cumulated_init_balance,
																 cumulated_balance))

					load_more_remaining -= 1
					load_more_counter -= 1

				if load_more_remaining > 0:
					# Load more line.
					lines.append(self._get_report_line_load_more(
							options,
							partner,
							self.MAX_LINES,
							load_more_remaining,
							cumulated_balance,
					))

		if not line_id:
			# Report total line.
			lines.append(self._get_report_line_total(
					options,
					total_initial_balance,
					total_debit,
					total_credit,
					total_balance
			))
		return lines

	def _get_reports_buttons(self):
		res = super()._get_reports_buttons()
		res.append({'name': _('Imprimer déplié'), 'sequence': 2, 'action': 'print_pdf_unfolded', 'file_export_type': _('PDF')})
		return res

	def print_pdf_unfolded(self, options):

		if not options.get('unfolded_lines', False):
			options['unfold_all_forced'] = False
			ctx = self._context.copy()
			ctx['balance_ctx'] = True
			self = self.with_context(ctx)
		else:
			options['unfolded_lines'] =[]
			options['unfold_all_forced'] = True
			for partner in options.get('partner_ids'):
				options['unfolded_lines'].append('partner_'+str(partner))
			options['unfold_all'] = True
		return {
			'type': 'ir_actions_account_report_download',
			'data': {'model'        : self.env.context.get('model'),
					 'options'      : json.dumps(options),
					 'output_format': 'pdf',
					 'financial_id' : self.env.context.get('id'),
					 }
		}
