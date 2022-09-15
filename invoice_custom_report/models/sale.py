# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_report_model_id = fields.Many2one('ir.actions.report', string="Modèle d'impression", domain="[('model', '=', 'sale.order')]")

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if vals.get('partner_id'):
            partner = self.env['res.partner'].sudo().browse(vals.get('partner_id'))
            if partner:
                if partner.sale_report_model_id:
                    res.sale_report_model_id = partner.sale_report_model_id.id

        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for rec in self:
            if vals.get('partner_id'):
                rec.sale_report_model_id =  rec.partner_id.sale_report_model_id.id
        return res
