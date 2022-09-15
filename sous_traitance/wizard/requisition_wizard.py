# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PurchaseRequisitionWizard(models.TransientModel):
    _name = 'purchase.requisition.wizard'

    supplier_ids = fields.Many2many('res.partner', string="Fournisseur")

    def create_purchase_requisition(self):
        so_ids = self.env['sale.order'].search([('id', 'in', self._context.get('active_ids', False)), ('requisition_id', '=', False)])
        if so_ids:
            type_id = self.env.ref('purchase_requisition.type_multi')
            if not type_id:
                type_id = self.env['purchase_requisition_type'].search([('exclusive', '=', 'multiple')], limit=1)
                if not type_id:
                    raise ValidationError("Merci de créer un type de conventions d'achat de type multiple")

            requisition_id = self.env['purchase.requisition'].create({'type_id':type_id.id,
                                                                      'origin': ','.join(so_ids.mapped('name'))
                                                                      })
            so_ids.write({'requisition_id':requisition_id.id })
            lines = so_ids.mapped('order_line').filtered(lambda r:r.soustraitance)
            if lines:
                for line in lines:
                    prix_soustraitance =line.price_unit
                    if line.product_id.marge_soutraitance:
                        prix_soustraitance = line.price_unit *(1 -line.product_id.marge_soutraitance)
                    self.env['purchase.requisition.line'].create({'product_id': line.product_id.id,
                                                                  'product_qty': line.product_uom_qty,
                                                                  'product_uom_id': line.product_uom.id,
                                                                  'price_unit':prix_soustraitance,
                                                                  'sale_line_id': line.id,
                                                                  'sale_price': line.price_unit,
                                                                  'requisition_id': requisition_id.id
                                                                  })
            requisition_id.action_in_progress()
            for partner in self.supplier_ids:
                purchase = self.env['purchase.order'].create({'requisition_id': requisition_id.id,
                                                              'partner_id': partner.id})
                purchase._onchange_requisition_id()


