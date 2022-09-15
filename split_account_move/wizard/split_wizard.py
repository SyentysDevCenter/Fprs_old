# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveLineSplitWizard(models.TransientModel):
    _name = 'account.move.line.split.wizard'

    line_ids = fields.One2many('account.move.line.split.wizard.line', 'wizard_id')
    line_id = fields.Many2one('account.move.line', 'Ecriture à scinder')
    company_id = fields.Many2one('res.company', related="line_id.company_id")
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    partner_id = fields.Many2one('res.partner', 'Partenaire', related="line_id.partner_id")
    name = fields.Char( 'Libellé', related="line_id.name")

    credit = fields.Monetary('Crédit', related="line_id.credit")
    debit = fields.Monetary('Débit', related="line_id.debit")
    account_id = fields.Many2one('account.account', 'Compte', related="line_id.account_id")

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        line = self.env['account.move.line'].browse(self.env.context.get('active_ids', False))
        if len(line)>1:
            raise ValidationError("Merci de ne sélectionner qu'une seule ligne")
        if line and (line.matched_debit_ids or line.matched_credit_ids or line.statement_id):
            raise ValidationError('Vous ne pouvez pas scinder une écriture lettrée ou rapprochée')
        res.update({'line_id': self.env.context.get('active_id', False)})
        return res

    def split_line(self):
        if sum(l.credit for l in self.line_ids) != self.credit:
            raise ValidationError('La somme des crédits et différente du crédit à scinder')
        if sum(l.debit for l in self.line_ids) != self.debit:
            raise ValidationError('La somme des débits et différente du debit à scinder')
        lines = []
        message = "Ecriture scindée, compte d'origine:" + str(self.account_id.code) + ' ' + str(
                self.account_id.name) + ' crédit: ' + str(self.credit) + ' débit: ' + str(self.debit) + ' en:  '+' <ul>'
        self.line_id.with_context(check_move_validity=False).write({'account_id': self.line_ids[0].account_id.id, 'partner_id': self.line_ids[0].partner_id.id,
                            'credit': self.line_ids[0].credit,'debit': self.line_ids[0].debit, 'name': self.line_ids[0].name})
        if self.line_ids[0].credit:
            message = message + '<li>[' + str(self.line_ids[0].account_id.code) + ']' + str(
                    self.line_ids[0].account_id.name) + ' _ crédit: ' + str(round(self.line_ids[0].credit, 2)) + ' </li>'
        if self.line_ids[0].debit:
            message = message + '<li>[' + str(self.line_ids[0].account_id.code) + ']' + str(
                    self.line_ids[0].account_id.name) + ' _ débit: ' + str(round(self.line_ids[0].debit, 2)) + ' </li>'

        if len(self.line_ids)>1:
            for line in self.line_ids[1:]:
                lines.append((0,0, {'account_id': line.account_id.id,
                                    'partner_id': line.partner_id.id,
                                    'credit': line.credit,
                                    'debit': line.debit,
                                    'move_id': self.line_id.move_id.id,
                                    'name': line.name
                                    }))
                if line.credit:
                    message = message + '<li>[' + str(line.account_id.code) + ']' + str(
                            line.account_id.name) + ' _ crédit: ' + str(
                        round(line.credit, 2)) + ' </li>'
                if line.debit:
                    message = message + '<li>[' + str(line.account_id.code) + ']' + str(
                            line.account_id.name) + ' _ débit: ' + str(
                        round(line.debit, 2)) + ' </li>'
        message = message + '</ul>'

        self.line_id.move_id.with_context(check_move_validity=False).write({'line_ids':lines })
        self.line_id.move_id.message_post(body=message)


class AccountMoveLineSplitWizardLine(models.TransientModel):
    _name = 'account.move.line.split.wizard.line'

    wizard_id = fields.Many2one('account.move.line.split.wizard')
    company_id = fields.Many2one('res.company', related = "wizard_id.company_id")
    currency_id = fields.Many2one('res.currency', related = "wizard_id.currency_id")
    account_id = fields.Many2one('account.account', 'Compte')
    partner_id = fields.Many2one('res.partner', 'Partenaire')
    credit = fields.Monetary('Crédit')
    debit = fields.Monetary('Débit')
    name = fields.Char()