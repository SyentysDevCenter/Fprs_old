# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.misc import format_date

class ProjectFinancierReport(models.AbstractModel):
	_name = "report.project_report.financier_report"


	@api.model
	def get_customer_invoice(self, project_ids, from_date, to_date):
		invoice_customer ={}
		for project_id in project_ids:
			sql_qr = """
					SELECT DISTINCT account_move.name AS "invoice_name" , 
							amount_total, 
							amount_total_signed,
							all_total_ht, 
							account_move_line.date, 
							res_partner.name AS "partner_name"
					FROM project_project
					INNER JOIN account_move_line ON project_project.analytic_account_id = account_move_line.analytic_account_id
					INNER JOIN account_move ON account_move_line.move_id = account_move.id
					INNER JOIN res_partner ON account_move.partner_id = res_partner.id
					WHERE account_move.move_type = 'out_invoice' 
							AND account_move_line.parent_state not in ('draft', 'cancel')
							AND project_project.id = %d
					
				""" % project_id

			if from_date:
				sql_qr += " AND account_move_line.date>=""" + "'" + str(from_date) + "'"

			if to_date:
				sql_qr += " AND account_move_line.date<=""" + "'" + str(to_date) + "'"

			sql_qr += " ORDER BY account_move_line.date ASC"""

			self.env.cr.execute(sql_qr)

			invoice_customer[project_id] = {'detail': [], 'total': 0.0, 'total_ht':0.0}
			detail = []
			total = 0
			total_ht = 0

			for invoice in self.env.cr.dictfetchall():
				detail.append(
					{
						'text': invoice['invoice_name'] + " du " + format_date(self.env, fields.Date.to_string(invoice['date']), date_format = 'dd/MM/yyyy')+ " - " + invoice['partner_name'],
						'amount': invoice['all_total_ht']
					}
				)
				total = total + invoice['amount_total']
				total_ht = total_ht + invoice['all_total_ht']

			invoice_customer[project_id]['detail'] = detail
			invoice_customer[project_id]['total'] = total
			invoice_customer[project_id]['total_ht'] = total_ht
		return invoice_customer

	@api.model
	def get_customer_invoice_refund(self, project_ids, from_date, to_date):
		invoice_customer_refund = {}
		for project_id in project_ids:
			sql_qr = """
						SELECT 	DISTINCT account_move.name AS "invoice_name",
								amount_total,
								amount_total_signed,
								all_total_ht,
								account_move_line.date,
								res_partner.name AS "partner_name"
						FROM project_project
						INNER JOIN account_move_line 
							ON project_project.analytic_account_id = account_move_line.analytic_account_id
						INNER JOIN account_move 
							ON account_move_line.move_id = account_move.id
						INNER JOIN res_partner 
							ON account_move.partner_id = res_partner.id
						WHERE account_move.move_type = 'out_refund' 
								AND account_move_line.parent_state not in ('draft', 'cancel')
								AND project_project.id = %d
					""" % project_id

			if from_date:
				sql_qr += " AND account_move_line.date>=""" + "'" + str(from_date) + "'"

			if to_date:
				sql_qr += " AND account_move_line.date<=""" + "'" + str(to_date) + "'"

			sql_qr += " ORDER BY account_move_line.date ASC"""

			self.env.cr.execute(sql_qr)

			invoice_customer_refund[project_id] = {'detail': [], 'total': 0.0, 'total_ht': 0.0}
			detail = []
			total = 0
			total_ht = 0

			for invoice in self.env.cr.dictfetchall():
				detail.append(
					{
						'text': invoice['invoice_name'] + " du " + format_date(self.env,
																			   fields.Date.to_string(invoice['date']),
																			   date_format='dd/MM/yyyy') + " - " +
								invoice['partner_name'],
						'amount': invoice['all_total_ht']
					}
				)
				total = total + invoice['amount_total']
				total_ht = total_ht + invoice['all_total_ht']

			invoice_customer_refund[project_id]['detail'] = detail
			invoice_customer_refund[project_id]['total'] = total
			invoice_customer_refund[project_id]['total_ht'] = total_ht
		return invoice_customer_refund

	@api.model
	def get_vendor_invoice(self, project_ids, from_date, to_date):
		invoice_vendor = {}
		for project_id in project_ids:
			# sql_qr = """
			# 			SELECT DISTINCT account_move.name AS "invoice_name" , amount_total, amount_total_signed,all_total_ht,
			# 			 account_move_line.date, res_partner.name AS "partner_name"
			# 			FROM project_project
			# 			INNER JOIN account_move_line ON project_project.analytic_account_id = account_move_line.analytic_account_id
			# 			INNER JOIN account_move ON account_move_line.move_id = account_move.id
			# 			INNER JOIN res_partner ON account_move.partner_id = res_partner.id
			# 			INNER JOIN account_journal ON account_journal.id = account_move.journal_id
			# 			WHERE account_move.move_type = 'in_invoice'
			# 					AND account_move_line.parent_state not in ('draft', 'cancel')
			# 					AND project_project.id = %d
			# 					AND account_journal.journal_sous_traitant is null
			# 		""" % project_id
			sql_qr = """
						select m.name AS "invoice_name", sum(aml.price_subtotal) as amount_total, m.date,r.name AS "partner_name"

from account_move_line aml left join account_move m on aml.move_id = m.id
							left join project_project p on p.analytic_account_id = aml.analytic_account_id
							left JOIN res_partner r ON m.partner_id = r.id
							left JOIN account_journal j ON j.id = m.journal_id
							WHERE m.move_type = 'in_invoice' 
									AND m.state not in ('draft', 'cancel')
									AND p.id = %s
									AND j.journal_sous_traitant is null
									and (aml.exclude_from_invoice_tab = false or aml.exclude_from_invoice_tab is null)
									group by m.name, m.date, r.name 
					""" % project_id

			if from_date:
				sql_qr += " AND m.date>=""" + "'" + str(from_date) + "'"

			if to_date:
				sql_qr += " AND m.date<=""" + "'" + str(to_date) + "'"

			sql_qr += " ORDER BY m.date ASC"""

			self.env.cr.execute(sql_qr)

			invoice_vendor[project_id] = {'detail': [], 'total': 0.0, 'total_ht': 0.0}
			detail = []
			total = 0
			total_ht = 0

			for invoice in self.env.cr.dictfetchall():
				detail.append(
					{
						'text':  invoice['invoice_name'] + " du " +format_date(self.env, fields.Date.to_string(invoice['date']), date_format = 'dd/MM/yyyy') + " - " + invoice['partner_name'],
						'amount': invoice['amount_total']
					}
				)
				total = total + invoice['amount_total']
				total_ht = total_ht + invoice['amount_total']

			invoice_vendor[project_id]['detail'] = detail
			invoice_vendor[project_id]['total'] = total
			invoice_vendor[project_id]['total_ht'] = total_ht
		return invoice_vendor

	@api.model
	def get_vendor_invoice_refund(self, project_ids, from_date, to_date):
		vendor_invoice_refund = {}
		for project_id in project_ids:
			# sql_qr = """
			# 			SELECT 	DISTINCT account_move.name AS "invoice_name",
			# 					amount_total,
			# 					amount_total_signed,
			# 					all_total_ht,
			# 					account_move_line.date,
			# 					res_partner.name AS "partner_name"
			# 			FROM project_project
			# 			INNER JOIN account_move_line
			# 				ON project_project.analytic_account_id = account_move_line.analytic_account_id
			# 			INNER JOIN account_move
			# 				ON account_move_line.move_id = account_move.id
			# 			INNER JOIN res_partner
			# 				ON account_move.partner_id = res_partner.id
			# 			WHERE account_move.move_type = 'in_refund'
			# 					AND account_move_line.parent_state not in ('draft', 'cancel')
			# 					AND project_project.id = %d
			# 		""" % project_id
			sql_qr = """
						select m.name AS "invoice_name", sum(aml.price_subtotal) as amount_total, m.date,r.name AS "partner_name"

from account_move_line aml left join account_move m on aml.move_id = m.id
							left join project_project p on p.analytic_account_id = aml.analytic_account_id
							left JOIN res_partner r ON m.partner_id = r.id
							left JOIN account_journal j ON j.id = m.journal_id
							WHERE m.move_type = 'in_refund' 
									AND m.state not in ('draft', 'cancel')
									AND p.id = %s
									AND (j.journal_sous_traitant = False or j.journal_sous_traitant is null)
									and (aml.exclude_from_invoice_tab = false or aml.exclude_from_invoice_tab is null)
									group by m.name, m.date, r.name
									
					""" % project_id

			if from_date:
				sql_qr += " AND m.date>=""" + "'" + str(from_date) + "'"

			if to_date:
				sql_qr += " AND m.date<=""" + "'" + str(to_date) + "'"

			sql_qr += " ORDER BY m.date ASC"""

			self.env.cr.execute(sql_qr)

			vendor_invoice_refund[project_id] = {'detail': [], 'total': 0.0, 'total_ht': 0.0}
			detail = []
			total = 0
			total_ht = 0

			for invoice in self.env.cr.dictfetchall():
				detail.append(
					{
						'text': invoice['invoice_name'] + " du " + format_date(self.env,
																			   fields.Date.to_string(invoice['date']),
																			   date_format='dd/MM/yyyy') + " - " +
								invoice['partner_name'],
						'amount': invoice['amount_total']
					}
				)
				total = total + invoice['amount_total']
				total_ht = total_ht + invoice['amount_total']

			vendor_invoice_refund[project_id]['detail'] = detail
			vendor_invoice_refund[project_id]['total'] = total
			vendor_invoice_refund[project_id]['total_ht'] = total_ht
		return vendor_invoice_refund

	@api.model
	def get_soustraitant_invoice(self, project_ids, from_date, to_date):
		invoice_vendor = {}
		for project_id in project_ids:
			# sql_qr = """
			# 				SELECT DISTINCT account_move.name AS "invoice_name" ,
			# 						amount_total,
			# 						amount_total_signed,
			# 						all_total_ht,
			# 				 account_move_line.date, res_partner.name AS "partner_name"
			# 				FROM project_project
			# 				INNER JOIN account_move_line ON project_project.analytic_account_id = account_move_line.analytic_account_id
			# 				INNER JOIN account_move ON account_move_line.move_id = account_move.id
			# 				INNER JOIN res_partner ON account_move.partner_id = res_partner.id
			# 				INNER JOIN account_journal ON account_journal.id = account_move.journal_id
			# 				WHERE account_move.move_type = 'in_invoice'
			# 						AND account_move_line.parent_state not in ('draft', 'cancel')
			# 						AND project_project.id = %d
			# 						AND account_journal.journal_sous_traitant = true
			# 			""" % project_id
			sql_qr = """
							select m.name AS "invoice_name", sum(aml.price_subtotal) as amount_total, m.date,r.name AS "partner_name"

from account_move_line aml left join account_move m on aml.move_id = m.id
							left join project_project p on p.analytic_account_id = aml.analytic_account_id
							left JOIN res_partner r ON m.partner_id = r.id
							left JOIN account_journal j ON j.id = m.journal_id
							WHERE m.move_type = 'in_invoice' 
									AND m.state not in ('draft', 'cancel')
									AND p.id = %s
									AND j.journal_sous_traitant = true
									and (aml.exclude_from_invoice_tab = false or aml.exclude_from_invoice_tab is null)
									group by m.name, m.date, r.name
									
						""" % project_id

			if from_date:
				sql_qr += " AND m.date>=""" + "'" + str(from_date) + "'"

			if to_date:
				sql_qr += " AND m.date<=""" + "'" + str(to_date) + "'"

			sql_qr += " ORDER BY m.date ASC"""

			self.env.cr.execute(sql_qr)

			invoice_vendor[project_id] = {'detail': [], 'total': 0.0, 'total_ht':0.0}
			detail = []
			total = 0
			total_ht = 0

			for invoice in self.env.cr.dictfetchall():
				detail.append(
						{
							'text'  : invoice['invoice_name'] + " du " + format_date(self.env,
																					 fields.Date.to_string(invoice['date']),
																					 date_format = 'dd/MM/yyyy') + " - " +
									  invoice['partner_name'],
							'amount': invoice['amount_total']
						}
				)
				total = total + invoice['amount_total']
				total_ht = total_ht + invoice['amount_total']

			invoice_vendor[project_id]['detail'] = detail
			invoice_vendor[project_id]['total'] = total
			invoice_vendor[project_id]['total_ht'] = total_ht
		return invoice_vendor


	@api.model
	def _get_report_values(self, docids, data = None):

		# customer invoices
		customer_invoice = self.get_customer_invoice(data['form']['project_id'], data['form']['from_date'], data['form']['to_date'])
		customer_invoice_refund = self.get_customer_invoice_refund(data['form']['project_id'], data['form']['from_date'], data['form']['to_date'])

		# vendor invoices
		vendor_invoice = self.get_vendor_invoice(data['form']['project_id'], data['form']['from_date'], data['form']['to_date'])
		vendor_invoice_refund = self.get_vendor_invoice_refund(data['form']['project_id'], data['form']['from_date'], data['form']['to_date'])

		# soustraitant_invoice
		soustraitant_invoice = self.get_soustraitant_invoice(data['form']['project_id'], data['form']['from_date'], data['form']['to_date'])

		docs = self.env['project.project'].browse(data['form']['project_id']).sudo()

		facture_fournisseur = {}
		facture_soustraitant = {}
		facture_client = {}
		timesheet_dict = {}
		expense_dict = {}
		divers_dict = {}
		total_cost_ht_proj = {}
		total_cost_proj = {}
		total_sale_proj = {}
		total_sale_ht_proj = {}
		prix_revient_marge_proj = {}
		revenu_prevu_amount_proj = {}
		percent_invoice_proj = {}
		coef_vente_proj = {}
		for project in docs:
			total_cost = 0.0
			total_cost_ht = 0.0
			total_sale = 0.0
			total_sale_ht = 0.0
			######Facture fournisseur

			if vendor_invoice:
				total_cost += vendor_invoice[project.id]['total']
				total_cost_ht += vendor_invoice[project.id]['total_ht']

			if vendor_invoice_refund:
				total_cost -= vendor_invoice_refund[project.id]['total']
				total_cost_ht -= vendor_invoice_refund[project.id]['total_ht']

			######Facture soustraitant

			if soustraitant_invoice:
				total_cost +=soustraitant_invoice[project.id]['total']
				total_cost_ht +=soustraitant_invoice[project.id]['total_ht']

			if customer_invoice:
				total_sale += customer_invoice[project.id]['total']
				total_sale_ht += customer_invoice[project.id]['total_ht']

			if customer_invoice_refund:
				total_sale -= customer_invoice_refund[project.id]['total']
				total_sale_ht -= customer_invoice_refund[project.id]['total_ht']

			######Main d'oeuvre
			timesheet_dict[project.id]={}
			timesheet_ids = self.env['account.analytic.line'].search([('project_id', '=', project.id), ('employee_id', '!=', False)])
			if timesheet_ids:
				timesheet_dict[project.id]['total_h'] = sum(l.unit_amount for l in timesheet_ids)
				timesheet_dict[project.id]['total_amount'] =sum(l.unit_amount * (l.employee_id.timesheet_cost) for l in timesheet_ids)
				total_cost += timesheet_dict[project.id]['total_amount']
				total_cost_ht += timesheet_dict[project.id]['total_amount']
			######Dépense
			expense_dict[project.id]={'detail':{}, 'total':0.0, 'total_ht': 0.0}
			expense_ids = self.env['hr.expense'].search([('analytic_account_id', '=', project.analytic_account_id.id)])
			if expense_ids:
				expense_dict[project.id]['total'] = sum(l.total_amount for l in expense_ids)
				expense_dict[project.id]['total_ht'] = sum(l.untaxed_amount for l in expense_ids)
				total_cost += expense_dict[project.id]['total']
				total_cost_ht += expense_dict[project.id]['total_ht']
				for l in expense_ids:
					if expense_dict[project.id]['detail'].get(l.product_id.name, False):
						expense_dict[project.id]['detail'][l.product_id.name]+= l.untaxed_amount
					else:
						expense_dict[project.id]['detail'][l.product_id.name] = l.untaxed_amount



			######frais divers
			divers_dict[project.id]={'detail':{}, 'total':0.0}
			divers_ids = self.env['account.analytic.line'].search([('account_id', '=', project.analytic_account_id.id),('amount', '<', 0),('type', '=', 'a'),
																   '|',
																   ('account_journal_id', '=', False),
																   ('account_journal_id.type', 'not in', ('sale', 'purchase'))])

			print('divers_idsdivers_ids', divers_ids)
			if divers_ids:
				divers_dict[project.id]['total'] = sum((-1) * l.amount for l in divers_ids)
				total_cost += divers_dict[project.id]['total']
				total_cost_ht += divers_dict[project.id]['total']
				for l in divers_ids:
					if l.general_account_id:
						if divers_dict[project.id]['detail'].get(l.general_account_id.display_name, False):
							divers_dict[project.id]['detail'][l.general_account_id.display_name]+= (-1) * l.amount
						else:
							divers_dict[project.id]['detail'][l.general_account_id.display_name] = (-1) * l.amount
					else:
						if divers_dict[project.id]['detail'].get(l.name, False):
							divers_dict[project.id]['detail'][l.name]+= (-1) * l.amount
						else:
							divers_dict[project.id]['detail'][l.name] = (-1) * l.amount
			print('divers_dictdivers_dict', divers_dict)

			# get initial amounts
			initial_amounts = dict()
			if len(docs) == 1:
				initial_amounts = {
					'initial_cost': docs[0].initial_cost,
					'initial_income': docs[0].initial_income,
				}
				total_cost_ht += docs[0].initial_cost
				total_sale_ht += docs[0].initial_income

			total_cost_ht_proj[project.id] = total_cost_ht
			total_cost_proj[project.id] = total_cost
			total_sale_proj[project.id] = total_sale
			total_sale_ht_proj[project.id] = total_sale_ht
			prix_revient_marge_proj[project.id] = total_cost * (1 + project.marge_souhaite/100)
			forecast_ids = self.env['account.analytic.line'].search([('account_id', '=', project.analytic_account_id.id),
																	 ('type', '=', 'f'),
																	 ('amount', '>', 0)])
			revenu_prevu_amount = sum(l.amount for l in forecast_ids)
			revenu_prevu_amount_proj[project.id] = revenu_prevu_amount
			percent_invoice_proj[project.id] = project.budget_ht and (total_sale_ht/project.budget_ht) or 0
			coef_vente_proj[project.id] = total_cost_ht and (total_sale_ht/total_cost_ht) or 0


		return {
			'doc_ids': data['form']['project_id'],
			'doc_model': 'project.project',
			'docs': docs,
			# 'facture_fournisseur':facture_fournisseur,
			'facture_fournisseur': vendor_invoice,
			'avoir_fournisseur': vendor_invoice_refund,
			'facture_soustraitant': soustraitant_invoice,
			# 'facture_client':facture_client,
			'facture_client': customer_invoice,
			'avoir_client': customer_invoice_refund,
			'timesheet_dict':timesheet_dict,
			'expense_dict': expense_dict,
			'divers_dict': divers_dict,
			'total_cost':total_cost_proj,
			'total_cost_ht':total_cost_ht_proj,
			'total_sale':total_sale_proj,
			'total_sale_ht':total_sale_ht_proj,
			'prix_revient_marge':prix_revient_marge_proj,
			'revenu_prevu_amount':revenu_prevu_amount_proj,
			'percent_invoice':percent_invoice_proj,
			'coef_vente':coef_vente_proj,
			'initial_amounts': initial_amounts,

		}
