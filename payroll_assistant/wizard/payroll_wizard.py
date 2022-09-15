# -*- coding: utf-8 -*-

import csv
from odoo import models, fields, api, _
import base64
import io
from odoo.exceptions import ValidationError
import logging
from odoo.tools.float_utils import  float_compare, float_round


import math

_logger = logging.getLogger(__name__)


class PayrollWizard(models.TransientModel):
    _name = 'payroll.wizard'
    _decsription = "Assistant création pièce comptable paie"

    file = fields.Binary('Fichier(.csv)', required=True)
    filename = fields.Char()
    date = fields.Date(string='Date', required=True)
    erreur_ids = fields.One2many('payroll.wizard.error', 'import_id')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    no_error = fields.Boolean(compute='compute_no_error', store=True)

    @api.depends('erreur_ids')
    def compute_no_error(self):
        for l in self:
            if not l.erreur_ids:
                l.no_error = True
            else:
                l.no_error = False

    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False



    def del_log(self):
        self.erreur_ids.unlink()
        return {
                'name': 'Assistant création pièce comptable paie',
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payroll.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }



    def import_account_move(self, data):
        if data.get('journal_id', False):
            move_data = {}
            move_data['name'] = data['name']
            move_data['journal_id'] = data['journal_id']
            move_data['company_id'] = self.env.user.company_id.id
            move_data['date'] = self.date
            move_data['move_type'] = 'entry'
            move_data['state'] = 'draft'
            move_data['currency_id'] = 1
            move_data['extract_state'] = 'no_extract_requested'
            move_data['invoice_line_ids'] = []
            move_data['line_ids'] = []
            invoice_lines = []
            for line in data['line_ids']:
                invoice_lines.append((0, 0, {
                    'exclude_from_invoice_tab': True,
                    'account_id': line[2]['account_id'],
                    'credit': float(line[2]['credit']),
                    'debit': float(line[2]['debit']),
                    'date': self.date,
                    'journal_id': data['journal_id'],
                    'currency_id': 1,
                    'company_currency_id': 1,
                    'company_id': self.env.user.company_id.id,
                    'balance': float(line[2]['debit']) - float(line[2]['credit']),
                    'name': str(line[2]['name']),

                }))
            new_invoice_id = self.env['account.move'].sudo().create(move_data)
            new_invoice_id.write({'invoice_line_ids': invoice_lines, })
            return new_invoice_id


    def test_import(self):
        csv_data = base64.b64decode(self.file)
        data_file = io.StringIO(csv_data.decode('ISO-8859-1', 'ignore'))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter=';')
        if not csv_reader:
            raise ValidationError("Veuillez joindre un fichier (.csv) avec un bon format s'il vous plaît !")
        data = {}
        data['name'] = "Pièce comptable paie"
        data['journal_id'] = self.journal_id.id
        data['line_ids'] = []
        totalcredit = totaldebit = 0
        file_reader.extend(csv_reader)
        for num, line in enumerate(file_reader):
            if num > 0:
                if not len(line) == 7:
                    self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                                   'erreur': "Ligne non conforme ."})]})
                else:
                    CompteNum = str(line[0])
                    print('CompteNum', CompteNum)
                    Libele = str(line[1])
                    Debit = str(line[3])
                    Credit = str(line[4])
                    # Debit = Debit.replace("|", "")
                    # Debit = Debit.replace("l", "")
                    Debit = Debit.replace(" ", "")
                    # Credit = Credit.replace("|", "")
                    # Credit = Credit.replace("l", "")
                    Credit = Credit.replace(" ", "")
                    Solde = str(line[5])
                    if CompteNum:
                        account_move_line_vals = {'exclude_from_invoice_tab': True}

                        if Debit:
                            if not self.isfloat(Debit):
                                self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                               'erreur': "le débit %s n'est pas un nombre réel " % (
                                                                   Debit)})]})
                            else:
                                account_move_line_vals['debit'] = float(Debit)
                                totaldebit += float(Debit)
                        else:
                            account_move_line_vals['debit'] = 0.0

                        if Credit:
                            if not self.isfloat(Credit):
                                self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                               'erreur': "le crédit %s n'est pas un nombre réel  !" % (
                                                                   Credit)})]})
                            else:
                                account_move_line_vals['credit'] = float(Credit)
                                totalcredit += float(Credit)
                        else:
                            account_move_line_vals['credit'] = 0.0


                        account_move_line_vals['name'] = Libele.replace("'"," ")
                        account_id = self.env['account.account'].sudo().search([('code', '=', CompteNum)], limit=1)
                        if account_id:
                            account_move_line_vals['account_id'] = account_id.id
                        else:
                            self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                               'erreur': "Le compte %s n'a pas été trouvé dans le système ." % (
                                                                   CompteNum)})]})

                        data['line_ids'].append((0, 0, account_move_line_vals))




        if float_compare(totalcredit, totaldebit, precision_rounding=0.01) != 0:
            self.write({'erreur_ids': [(0, 0, {'ligne': 'REMARQUE',
                                                   'erreur': "le total débit est différent du total crédit (Pièce comptable non équilibrée)"}),(0, 0, {'ligne': 'TOTAL DEBIT',
                                                                   'erreur': "%s" % (
                                                                       totaldebit)}),(0, 0, {'ligne': 'TOTAL CREDIT',
                                                                   'erreur': "%s" % (
                                                                       totalcredit)})]})
        return {
            'name': 'Assistant création pièce comptable paie',
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payroll.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


    def import_payroll(self):
        csv_data = base64.b64decode(self.file)
        data_file = io.StringIO(csv_data.decode('ISO-8859-1', 'ignore'))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter=';')
        if not csv_reader:
            raise ValidationError("Veuillez joindre un fichier (.csv) avec un bon format s'il vous plaît !")
        data = {}
        data['name'] = "Pièce comptable paie"
        data['journal_id'] = self.journal_id.id
        data['line_ids'] = []
        file_reader.extend(csv_reader)
        totaldebit = totalcredit = 0
        for num, line in enumerate(file_reader):
            if num > 0:
                print('linelineline', line)
                if not len(line) == 6:
                    self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                               'erreur': "Ligne non conforme ."})]})
                else:
                    CompteNum = str(line[0])
                    print('CompteNum', CompteNum)

                    Libele = str(line[1])
                    Debit = str(line[3])
                    # Debit = Debit.replace("|", "")
                    # Debit = Debit.replace("l", "")
                    Debit = Debit.replace(" ", "")
                    Credit = str(line[4])
                    # Credit = Credit.replace("|", "")
                    # Credit = Credit.replace("l", "")
                    Credit = Credit.replace(" ", "")
                    Solde = str(line[5])
                    if CompteNum:
                        account_move_line_vals = {'exclude_from_invoice_tab': True}
                        if Debit:
                            if not self.isfloat(Debit):
                                self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                                   'erreur': "le débit %s n'est pas un nombre réel " % (
                                                                       Debit)})]})
                            else:
                                account_move_line_vals['debit'] = float(Debit)
                                totaldebit += float(Debit)
                        else:
                            account_move_line_vals['debit'] = 0.0

                        if Credit:
                            if not self.isfloat(Credit):
                                self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                                   'erreur': "le crédit %s n'est pas un nombre réel  !" % (
                                                                       Credit)})]})
                            else:
                                account_move_line_vals['credit'] = float(Credit)
                                totalcredit += float(Credit)
                        else:
                            account_move_line_vals['credit'] = 0.0

                        account_move_line_vals['name'] = Libele.replace("'"," ")
                        account_id = self.env['account.account'].sudo().search([('code', '=', CompteNum)], limit=1)
                        if account_id:
                            account_move_line_vals['account_id'] = account_id.id
                        else:
                            self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                               'erreur': "Le compte %s n'a pas été trouvé dans le système ." % (
                                                                   CompteNum)})]})
                        data['line_ids'].append((0, 0, account_move_line_vals))
        print('totalcredittotalcredit', float_round(totalcredit,2),  float_round(totaldebit,2), float_compare(float_round(totalcredit,2), float_round(totaldebit,2), precision_rounding=0.01))
        if float_compare(float_round(totalcredit,2), float_round(totaldebit,2), precision_rounding=0.01) == 0:
            if not self.erreur_ids:
                move_id = self.import_account_move(data)
                tree_view = self.env.ref('account.view_move_tree').id
                form_view = self.env.ref('account.view_move_form').id
                return {
                    'name'     : 'Pièce comptable',
                    'view_mode': 'form, tree',
                    'view_id': form_view,
                    'views': [(form_view, 'form'),(tree_view, 'tree')],
                    'res_model': 'account.move',
                    'res_id': move_id.id,
                    'domain'   : [('id', '=', move_id.id)],
                    'type'     : 'ir.actions.act_window'
                }
                # return {'type': 'ir.actions.act_window_close'}
            else:
                return {
                    'name': 'Assistant création pièce comptable paie',
                    'context': self.env.context,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'payroll.wizard',
                    'res_id': self.id,
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }

        else:
            self.write({'erreur_ids': [(0, 0, {'ligne': 'REMARQUE',
                                                   'erreur': "le total débit est différent du total crédit (Pièce comptable non équilibrée)"}),(0, 0, {'ligne': 'TOTAL DEBIT',
                                                                   'erreur': "%s" % (
                                                                       totaldebit)}),(0, 0, {'ligne': 'TOTAL CREDIT',
                                                                   'erreur': "%s" % (
                                                                       totalcredit)})]})

            return {
                'name': 'Assistant création pièce comptable paie',
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payroll.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }







class PayrollWizardError(models.TransientModel):
    _name = 'payroll.wizard.error'
    _description = "Assistant création pièce comptable paie erreur"

    import_id = fields.Many2one('payroll.wizard')
    ligne = fields.Char('Ligne')
    erreur = fields.Char('Message')