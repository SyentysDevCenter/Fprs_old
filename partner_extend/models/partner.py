# -*- coding: utf-8 -*-


from odoo import api, fields, models

class ResPartner(models.Model):
	_inherit = 'res.partner'

	sous_traitant = fields.Boolean('Sous traitant')
	property_account_rg_id = fields.Many2one('account.account', company_dependent = True,
													 string = "Compte de retenue de garantie",
													 domain = "[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
													 )
	property_account_fin_rg_id = fields.Many2one('account.account', company_dependent = True,
													 string = "Compte de RG fin de travaux",
													 domain = "[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
													 )
	old_account = fields.Char('Ancien compte')
	# project_ids = fields.One2many('project.project', 'partner_id', 'Chantiers')
	partner_projects_count = fields.Integer(string='Chantiers', compute='_compute_projects_count')

	def _compute_projects_count(self):
		for rec in self:
			project_ids = self.env['project.project'].sudo().search([('partner_id', '=', rec.id)])
			rec.partner_projects_count = len(project_ids)

	def partner_projects_action(self):
		self.ensure_one()
		action = {
			'name': 'Chantiers',
			'type': 'ir.actions.act_window',
			'res_model': 'project.project',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'context': {'default_partner_id': self.id},
			'domain': [('partner_id', '=', self.id)],
			'target': 'current',
		}
		return action


class AccountPaymentTerm(models.Model):
	_inherit = 'account.payment.term'

	code = fields.Char('Code')