# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contract_count = fields.Integer(compute='compute_contract_count')




    def compute_contract_count(self):
        for rec in self:
            rec.contract_count = 0
            all_contracts = self.env['sale.contract'].search(['|', ('customer_ids', 'in', self.id), ('customer_id', '=', self.id)])
            if all_contracts:
                rec.contract_count = len(all_contracts)


    def view_partner_contracts(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Contrats',
            'res_model': 'sale.contract',
            'view_mode': 'tree,form',
            'domain': ['|', ('customer_ids', 'in', self.id), ('customer_id', '=', self.id)],
            'context': dict(self._context, create=False, default_company_id=self.env.company.id),
        }


