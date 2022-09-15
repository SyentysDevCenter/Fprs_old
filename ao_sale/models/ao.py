# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    # def get_default_ao_product(self):
    #     template_id = self.env.ref('ao_sale.ao_invoicable_product')
    #     if template_id:
    #         product = self.env['product.product'].search([('product_tmpl_id', '=', template_id.id)])[0].id
    #         return product

    ao_product_id = fields.Many2one('product.product',
                                     string='Produit de facturation des AO')


class Ao(models.Model):
    _inherit = 'ao.ao'

    sale_ids = fields.One2many('sale.order', 'ao_id', 'Devis/commandes')
    sale_count = fields.Integer('#Devis/Commande', compute='compute_sale_count', store=True)

    @api.depends('sale_ids')
    def compute_sale_count(self):
        for rec in self:
            rec.sale_count = len(rec.sale_ids)

    def view_ao_sales(self):
            for rec in self:
                return { "type": "ir.actions.act_window",
                        "res_model": "sale.order",
                        "domain": [("ao_id", "=", rec.id)],
                        "context": {'default_ao_id': rec.id,
                                    'default_partner_id':rec.partner_id and rec.partner_id.id,
                                    'default_chantier_id': rec.project_id and rec.project_id.id or False
                },
                        "name": "Devis/Commande",
                         "view_mode": 'tree,form'
                         }

    def ao_create_sale(self):
        product = self.env.user.company_id.ao_product_id
        for rec in self:
            if not rec.partner_id:
                raise ValidationError('Vous ne pouvez pas créer un devis pour un AO sans client!')
            sale_id = self.env['sale.order'].create({'partner_id': rec.partner_id.id,
                                                     'date_order': fields.Date.context_today(self),
                                                     'ao_id': rec.id,
                                                     'chantier_id': rec.project_id and rec.project_id.id or False
                                                     })
            for line in rec.project_id.wbs_ids.filtered(lambda r:r.is_invoicable):
                if not line.product_id and not product:
                    raise ValidationError('Aucun article de facturation trouvé pour la ligne %s!'%(line.complete_name))
                else:
                    product_to_use = line.product_id or product
                self.env['sale.order.line'].create({'product_id': product_to_use.id,
                                                    'name': line.name,
                                                    'price_unit': line.unit_price,
                                                    'product_uom_qty': line.qty,
                                                    'product_uom': product_to_use.uom_id.id,
                                                    'order_id': sale_id.id
                                                    })
            return { "type": "ir.actions.act_window",
                        "res_model": "sale.order",
                        "domain": [("id", "=", sale_id.id)],
                        "name": "Devis/Commande",
                         "view_mode": 'tree,form'}

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ao_id = fields.Many2one('ao.ao', 'AO')

