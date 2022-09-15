# -*- coding: utf-8 -*-

from odoo import api, fields, models
from collections import defaultdict

class AccountMove(models.Model):
    _inherit = 'account.move'

    tax_lines = fields.One2many('account.move.tax.line', 'move_id', )


    # def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
    #     super(AccountMove, self)._recompute_dynamic_lines()
    #     self.compute_tax_lines()

    @api.model_create_multi
    def create(self, vals_list):
        rslt = super(AccountMove, self).create(vals_list)
        for i, vals in enumerate(vals_list):
            if 'line_ids' in vals or 'invoice_line_ids' in vals:
                rslt[i].compute_tax_lines()
        return rslt\

    def write(self, vals):
        rslt = super(AccountMove, self).write(vals)
        for move in self:
            if 'line_ids' in vals or 'invoice_line_ids' in vals:
                move.compute_tax_lines()
        return rslt

    def compute_tax_lines(self):
        ''' Helper to get the taxes grouped according their account.tax.group.
        This method is only used when printing the invoice.
        '''
        for move in self:
            move.tax_lines.unlink()

            lang_env = move.with_context(lang=move.partner_id.lang).env
            balance_multiplicator = -1 if move.is_inbound() else 1

            tax_lines = move.line_ids.filtered('tax_line_id')
            base_lines = move.line_ids.filtered('tax_ids')

            tax_group_mapping = defaultdict(lambda: {
                'base_lines': set(),
                'base_amount': 0.0,
                'tax_amount': 0.0,
            })

            # Compute base amounts.
            for base_line in base_lines:
                base_amount = balance_multiplicator * (base_line.amount_currency if base_line.currency_id else base_line.balance)

                for tax in base_line.tax_ids.flatten_taxes_hierarchy():

                    if base_line.tax_line_id.tax_group_id == tax.tax_group_id:
                        continue

                    tax_group_vals = tax_group_mapping[tax.tax_group_id]
                    if base_line not in tax_group_vals['base_lines']:
                        tax_group_vals['base_amount'] += base_amount
                        tax_group_vals['base_lines'].add(base_line)

            # Compute tax amounts.
            for tax_line in tax_lines:
                tax_amount = balance_multiplicator * (tax_line.amount_currency if tax_line.currency_id else tax_line.balance)
                tax_group_vals = tax_group_mapping[tax_line.tax_line_id.tax_group_id]
                tax_group_vals['tax_amount'] += tax_amount

            tax_groups = sorted(tax_group_mapping.keys(), key=lambda x: x.sequence)
            for tax_group in tax_groups:
                tax_group_vals = tax_group_mapping[tax_group]

                tax = self.env['account.move.tax.line'].create({'tax_id': tax_group.id,
                                           'tax': tax_group_vals['tax_amount'],
                                           'base': tax_group_vals['base_amount'],
                                           'move_id': move.id})



class AccountMoveTaxLine(models.Model):
    _name= 'account.move.tax.line'

    move_id = fields.Many2one('account.move')
    tax_id = fields.Many2one('account.tax.group')
    tax_amount = fields.Float(compute="compute_tax_amount", store=True)
    amount = fields.Float()
    base = fields.Float()
    tax = fields.Float()

    @api.depends('tax_id')
    def compute_tax_amount(self):
        for rec in self:
            if rec.tax_id:
                tax = self.env['account.tax'].search([('tax_group_id', '=', rec.tax_id.id)])
                if tax:
                    rec.tax_amount = tax[0].amount