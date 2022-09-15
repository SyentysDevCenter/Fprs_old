from odoo import api, fields, models


class UpdateAccountAccount(models.TransientModel):
    _name = 'update.account.account.wizard'
    _description = "Update account"

    account_id = fields.Many2one('account.account', string='Compte', required=True)
    line_ids = fields.One2many('update.account.account.wizard.line', 'wizard_id')

    def update(self):
        if self.line_ids:
            q = """UPDATE account_move_line SET account_id= %(account_id)s WHERE id in %(ids)s"""
            self.env.cr.execute(q, {'ids': tuple(self.line_ids.mapped('move_line_id').mapped('id')), 'account_id': self.account_id.id})
        return {'type': 'ir.actions.act_window_close'}


class UpdateAccountAccountLine(models.TransientModel):
    _name = 'update.account.account.wizard.line'
    _description = "Update account account"


    wizard_id = fields.Many2one('update.account.account.wizard')
    move_line_id = fields.Many2one('account.move.line', string="Écriture comptable")
    account_id = fields.Many2one('account.account', related='move_line_id.account_id', string='Compte', store=True)
    journal_id = fields.Many2one('account.journal', related='move_line_id.journal_id', string='Journal', store=True)
    move_id = fields.Many2one('account.move', related='move_line_id.move_id', store=True, string='Pièce comptable')


