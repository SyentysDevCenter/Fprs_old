from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    all_total_ht = fields.Monetary(string='Montant total hors taxe', store=True, compute='_compute_all_total',
                                   currency_field='company_currency_id')
    total_gr = fields.Monetary(string='Montant retenue de garantie', store=True, compute='_compute_all_total',
                               currency_field='company_currency_id')

    @api.depends('invoice_line_ids', 'invoice_line_ids.price_subtotal', 'amount_untaxed')
    def _compute_all_total(self):
        for move in self:
            rg_prices = move.invoice_line_ids.filtered(lambda line: line.product_id.is_garantie_retenue == True).mapped(
                'price_subtotal')
            move.total_gr = sum(abs(price) for price in rg_prices)
            move.all_total_ht = move.total_gr + move.amount_untaxed
