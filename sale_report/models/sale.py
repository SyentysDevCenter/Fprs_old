from odoo.addons import decimal_precision as dp
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sales Order'

    date_edition = fields.Datetime(required=True, default=fields.Date.context_today)
    # creteil_text = fields.Text(string='Texte Créteil')
    creteil_text = fields.Html('Texte Créteil')
    description = fields.Text(string='Description')


    # marche = fields.Char(string='marche',compute='get_partner_acti_marche')
    #
    #
    # def get_partner_acti_marche(self):
    #     for record in self:
    #         partner_contrat = self.env['sale.contract'].search([('customer_id','=',self.partner_id.id),('type','=','marche'),('contract_actif','=',True)], limit=1)
    #         print('partner',partner_contrat)
    #         self.marche = partner_contrat.name
    #             # return partner_contrat.name
    #     return


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _description = 'Sales Order Line'

    taxes_amount = fields.Float(compute='_compute_taxes_amount', readonly=True, store=True, digits='Product Price')
    taux_tva = fields.Float('taux_tva')

    def get_designation(self):
        print(self.name)
        if '[' in self.product_id.name:
            return self.product_id.name[:self.name.find('[')]

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_taxes_amount(self):
        for line in self:
            if line.tax_id:
                taxes = line.tax_id
                if taxes:
                    if len(taxes) == 1:
                        line.taxes_amount = line.price_subtotal * (taxes.amount / 100)
                        line.taux_tva = taxes.amount
                    else:
                        total_amount = 0
                        for tax in line.tax_id:
                            print(tax.amount)
                            print(tax.name)
                            total_amount += tax.amount
                            print(total_amount)
                            line.taux_tva = total_amount
                        line.taxes_amount = line.price_subtotal * (total_amount / 100)
                        print(line.taxes_amount)


