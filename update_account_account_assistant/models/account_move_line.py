from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def update_account_lunch_wizard(self):
        lines = []
        account_move_lines = self.env['account.move.line'].browse(self._context.get('active_ids', False))
        if any(l.matched_debit_ids or l.matched_credit_ids or l.full_reconcile_id for l in account_move_lines):
            raise ValidationError("Vous ne pouvez pas changer le compte d'une écriture lettré")
        if account_move_lines:
            move_ids = account_move_lines.mapped('move_id')
            if move_ids:
                if any(l.move_type != 'entry' for l in move_ids):
                    raise ValidationError("Veuillez ne sélectionner que les opérations diverses")

                else:
                    for line in account_move_lines:
                        vals = (0, 0, {
                            'move_line_id': line.id,
                        })
                        lines.append(vals)

        action = self.env.ref('update_account_account_assistant.update_account_wizard_action').read()[0]
        action['views'] = [
            (self.env.ref('update_account_account_assistant.update_account_account_form_view').id, 'form')]
        action['context'] = {'default_line_ids': lines}

        return action
