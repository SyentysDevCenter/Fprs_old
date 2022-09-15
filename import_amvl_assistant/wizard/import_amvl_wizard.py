# -*- coding: utf-8 -*-

import csv
from odoo import models, fields, api, _
import base64
import io
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ImportAccountMoveLineWizard(models.TransientModel):
    _name = 'account.move.line.import.wizard'

    file = fields.Binary('Fichier(.csv)', required=True)
    erreur_ids = fields.One2many('account.move.line.import.wizard.line', 'import_id')
    executed = fields.Boolean()

    def post_moves(self):
        self.env.cr.execute("""SELECT count(*) from account_move where importe_fec = True and state ='draft';""")
        len_moves = self.env.cr.fetchone()[0]
        i = 0
        print('len_moves', len_moves)
        while i <len_moves:
            i += 1000
            moves = self.env['account.move'].search([('importe_fec', '=', True), ('state', '=', 'draft')], limit=i)
            moves.action_post()
            self.env.cr.commit()

    def reconcile_imported_move_lines(self):
        """ Reconcile imported move lines, the matching is done between the fields ['account_id', 'matching_number'] """

        # Ensure that the database is aligned
        moves = self.env['account.move'].search([('importe_fec', '=', True)])
        moves.flush()

        # Retrieve the move lines
        sql = """ SELECT ARRAY_AGG(id) ids,
                         account_id
                    FROM account_move_line
                   WHERE account_id IS NOT NULL
                         AND fec_matching_number IS NOT NULL
                         AND reconciled = False
                         AND move_id in %s
                GROUP BY account_id, fec_matching_number
                  HAVING COUNT(*) > 1 """

        # Set the account as reconcilable and actively reconcile the lines
        self.env.cr.execute(sql, (tuple(moves.ids), ))
        for record in self.env.cr.fetchall():
            matched_move_line_ids, account_id = record
            self.env["account.account"].browse([account_id]).reconcile = True
            self.env["account.move.line"].browse(matched_move_line_ids).with_context(no_exchange_difference=True).reconcile()

    def del_log(self):
        if self.erreur_ids:
            self.erreur_ids.sudo().unlink()

        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move.line.import.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def test(self):

        csv_data = base64.b64decode(self.file)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter='|')
        if not csv_reader:
            raise ValidationError("Veuillez joindre un fichier (.csv) avec un bon format s'il vous plaît !")

        file_reader.extend(csv_reader)
        for num, line in enumerate(file_reader):
            if num > 0:
                if not len(line) == 20:
                    raise ValidationError(_('Le fichier inséré a une mauvaise format !, ligne %s', num + 1))
                account_move_line_vals = {}
                JournalCode = str(line[0])
                JournalLib = str(line[1])
                EcritureNum = str(line[2])
                EcritureDate = line[3]
                CompteNum = str(line[4])
                CompteLib = str(line[5])
                CompAuxNum = line[6]
                CompAuxLib = line[7]
                PieceRef = str(line[8])
                PieceDate = line[9]
                EcritureLib = str(line[10])
                Montant = str(line[11])
                if Montant.find(','):
                    Montant = Montant.replace(",",".")
                Montant = float(Montant)
                Sens = float(line[12])
                EcritureLet = str(line[13])
                DateLet = line[14]
                ValidDate = line[15]
                Idevise = line[17]

                if JournalCode:
                    journal_id = self.env['account.journal'].sudo().search([]).filtered(lambda x: x.code and x.code.strip() == JournalCode.strip())
                    if journal_id:
                        account_move_line_vals['journal_id'] = journal_id[0].id
                    else:
                        self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                           'erreur': "Le journal n'a pas été trouvé dans le système !"})]})

                if EcritureNum:
                    account_move_line_vals['ref'] = EcritureNum



                if CompteNum:
                    account_id = self.env['account.account'].sudo().search([]).filtered(lambda x: x.code and x.code.strip() == CompteNum.strip())
                    if account_id:
                        account_move_line_vals['account_id'] = account_id[0].id
                    else:
                        self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                           'erreur': "Le compte n'a pas été trouvé dans le système, il va être ajouté ."})]})


                if EcritureLib:
                    account_move_line_vals['name'] = EcritureLib

                if Sens > 0:
                    account_move_line_vals['debit'] = Montant or 0.0
                    account_move_line_vals['credit'] = 0.0

                else:
                    account_move_line_vals['credit'] = Montant or 0.0
                    account_move_line_vals['debit'] = 0.0

                # if Idevise:
                #     currency_id = self.env['res.currency'].sudo().search([]).filtered(lambda x: x.name and x.name.strip() == Idevise.strip() or x.name[0] == Idevise.strip())
                #     if currency_id:
                #         account_move_line_vals['currency_id'] = currency_id.id
                #     else:
                #         self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                #                                            'erreur': "La Devise n'a pas été trouvée dans le système !"})]})


        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move.line.import.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }




    def import_account_move_line(self):
        self.executed = True
        csv_data = base64.b64decode(self.file)
        data_file = io.StringIO(csv_data.decode("ISO-8859-1"))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter='|')
        if not csv_reader:
            raise ValidationError("Veuillez joindre un fichier (.csv) avec un bon format s'il vous plaît !")

        file_reader.extend(csv_reader)
        to_reconcile = {}
        company_id = self.env.user.company_id.id
        data = {}
        accounts = {}
        account_ids = self.env['account.account'].sudo().search([])
        for acc in account_ids:
            accounts[acc.code.strip()] = acc.id

        journals = {}
        journal_ids = self.env['account.journal'].sudo().search([])
        for jo in journal_ids:
            journals[jo.code.strip()] = jo.id



        for num, line in enumerate(file_reader):
            print('ddddddddddd222', len(line),num)

            if num > 0:
                if not len(line) == 20:
                    print('ddddddddddd', len(line))
                    raise ValidationError(_('Le fichier inséré a une mauvaise format !, ligne %s', num + 1))
                JournalCode = str(line[0])
                JournalLib = str(line[1])
                EcritureNum = str(line[2])
                EcritureDate = line[3]
                CompteNum = str(line[4])
                CompteLib = str(line[5])
                CompAuxNum = line[6]
                CompAuxLib = line[7]
                PieceRef = str(line[8])
                PieceDate = line[9]
                EcritureLib = str(line[10])
                Montant = str(line[11])
                if Montant.find(','):
                    Montant = Montant.replace(",",".")
                Montant = float(Montant)
                Sens = float(line[12])
                EcritureLet = str(line[13])
                DateLet = line[14]
                ValidDate = line[15]
                Idevise = line[17]
                account_move_line_vals = {'exclude_from_invoice_tab': True, 'fec_matching_number':  EcritureLet or False}


                if CompteNum:
                    # account_id = self.env['account.account'].sudo().search([]).filtered(lambda x: x.code and x.code.strip() == CompteNum.strip())
                    if accounts.get(CompteNum.strip(),False):
                        account_move_line_vals['account_id'] = accounts[CompteNum.strip()]
                    else:
                        self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                           'erreur': "Le compte n'a pas été trouvé dans le système, il va être ajouté ."})]})
                        type = self.env.ref('account.data_account_type_equity').id
                        reconcile= False
                        code_compte = CompteNum.strip()
                        if code_compte.startswith('281'):
                            type = self.env.ref('account.data_account_type_fixed_assets')
                        if code_compte.startswith('401'):
                            type = self.env.ref('account.data_account_type_payable')
                            reconcile= True

                        if code_compte.startswith('41'):
                            type = self.env.ref('account.data_account_type_receivable')
                            reconcile= True
                        if code_compte.startswith('43') or code_compte.startswith('46') :
                            type = self.env.ref('account.data_account_type_current_liabilities')
                        if code_compte.startswith('51') :
                            type = self.env.ref('account.data_account_type_liquidity')
                        if code_compte.startswith('6') :
                            type = self.env.ref('account.data_account_type_expenses')
                        if code_compte.startswith('7') :
                            type = self.env.ref('account.data_account_type_revenue')



                        account_account_vals = {
                            'code': CompteNum.strip(),
                            'name': CompteLib,
                            'company_id': self.env.user.company_id.id,
                            'user_type_id': type.id,
                            'cree_fec': True,
                            # 'allowed_journal_ids': [(6, 0, self.env['account.journal'].search([]).ids)]
                        }
                        if EcritureLet or reconcile:
                            account_account_vals['reconcile'] = True
                        account_id = self.env['account.account'].sudo().create(account_account_vals)
                        accounts[account_id.code] = account_id.id
                        if account_id:
                            account_move_line_vals['account_id'] = account_id.id


                if EcritureLib:
                    account_move_line_vals['name'] = EcritureLib.replace("'", '"')

                if EcritureNum:
                    account_move_line_vals['ref'] = EcritureNum

                if Sens > 0:
                    if Montant>0:
                        account_move_line_vals['debit'] = Montant or 0.0
                        account_move_line_vals['credit'] = 0.0
                    else:
                        account_move_line_vals['credit'] = (-1)*Montant or 0.0
                        account_move_line_vals['debit'] = 0.0

                else:
                    if Montant>0:

                        account_move_line_vals['credit'] = Montant or 0.0
                        account_move_line_vals['debit'] = 0.0
                    else:
                        account_move_line_vals['debit'] = (-1)*Montant or 0.0
                        account_move_line_vals['credit'] = 0.0

                # if Idevise:
                #     currency_id = self.env['res.currency'].sudo().search([]).filtered(lambda x: x.name and x.name.strip() == Idevise.strip() or x.name[0] == Idevise.strip())
                #     if currency_id:
                #         account_move_line_vals['currency_id'] = currency_id.id
                #     else:
                #         self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                #                                            'erreur': "La Devise n'a pas été trouvée dans le système !"})]})

                if EcritureNum not in data.keys():
                    data[EcritureNum] = {}
                    data[EcritureNum]['line_ids'] = [(0, 0, account_move_line_vals)]
                    if JournalCode:
                        # journal_id = self.env['account.journal'].sudo().search([]).filtered(
                        #     lambda x: x.code and x.code.strip() == JournalCode.strip())
                        if journals.get(JournalCode.strip(), False):
                            data[EcritureNum]['journal_id'] = journals[JournalCode.strip()]

                        else:
                            self.write({'erreur_ids': [(0, 0, {'ligne': num + 1,
                                                               'erreur': "Le journal n'a pas été trouvé dans le système !"})]})
                    if EcritureNum:
                        data[EcritureNum]['ref'] = EcritureNum
                    data[EcritureNum]['importe_fec'] = True
                    if PieceDate:
                        date = PieceDate
                        year = date[:4]
                        month = date[4:6]
                        day = date[6:8]
                        date_string = year + '-' + month + '-' + day
                        date_string2 = '-'.join([str(year), str(month),str(day) ])
                        move_date = fields.Date.from_string(date_string)
                        data[EcritureNum]['date'] = move_date
                        data[EcritureNum]['date_string'] = date_string2

                else:
                    data[EcritureNum]['line_ids'].append((0, 0, account_move_line_vals))

                if EcritureLet and CompteNum:
                    if len(to_reconcile) == 0:
                            to_reconcile[tuple([CompteNum,EcritureLet])] = [EcritureNum]
                    else:
                        if tuple([CompteNum,EcritureLet]) not in to_reconcile:
                            to_reconcile[tuple([CompteNum, EcritureLet])] = [EcritureNum]
                        else:
                            to_reconcile[tuple([CompteNum,EcritureLet])].append(EcritureNum)
        # records = []
        # all_records ={}
        # if len(data) != 0:
        #     for move in data:
        #         records.append({"values": move})
        # all_records['account.move'] = self.env['account.move']._load_records(records)
        # moves = all_records.get("account.move", [])


        if len(data) != 0:
            # for move in data:
            _logger.info("start creating moves..."+str(len(data)))

            # moves = self.env['account.move'].sudo().with_context(check_move_validity=False).create(data.values())
            move_ids= []
            for move in data:
                print('rrrrrrrrr', data[move])
                if data[move].get('journal_id',False ):
                    self.env.cr.execute("""INSERT INTO account_move (journal_id, ref,company_id, importe_fec, date , move_type, state,currency_id, extract_state) 
                    values (%s,%s, %s, True,'%s','entry', 'draft',1, 'no_extract_requested') returning id;"""
                                        %(data[move]['journal_id'], data[move]['ref'], company_id,data[move]['date_string']))
                    move_id = self.env.cr.fetchone()[0]
                    move_ids.append(move_id)
                    for line in data[move]['line_ids']:
                        self.env.cr.execute(
                            """INSERT INTO account_move_line (account_id, credit, debit,fec_matching_number, date ,journal_id, move_id, ref,currency_id,company_currency_id, company_id, balance, importe_fec, name)
                             values (%s,%s,%s, '%s','%s',%s,%s ,%s,1,1,%s,%s, True,'%s') returning id;"""
                            % (line[2]['account_id'], line[2]['credit'],line[2]['debit'], str(line[2]['fec_matching_number']), data[move]['date_string'],
                               data[move]['journal_id'], move_id, line[2]['ref'], company_id, line[2]['debit']-line[2]['credit'], str(line[2]['name'])))
                # if create_account_move:
                #     # create_account_move.sudo().write({'ref': data[move]['ref'], 'state': 'posted'})
                #     create_account_move.action_post()
            moves = self.env['account.move'].browse(move_ids)
        # if moves:
        #     _logger.info("Posting moves..."+str(len(moves)))
        #     moves.action_post()
        #     _logger.info("Reconciling move_lines...")
        #     self._reconcile_imported_move_lines(moves)

        # if len(to_reconcile) != 0:
        #     for element in to_reconcile.values():
        #         move_lines = self.env['account.move.line'].sudo().search([]).filtered(lambda x: x.move_id and x.move_id.ref and x.move_id.state == 'posted' and x.move_id.ref in element)
        #         if move_lines:
        #             move_lines.reconcile()

        if self.erreur_ids:
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move.line.import.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            return {'type': 'ir.actions.act_window_close'}


class ImportAccountMoveLineWizardLine(models.TransientModel):
    _name = 'account.move.line.import.wizard.line'

    import_id = fields.Many2one('account.move.line.import.wizard')
    ligne = fields.Char('Ligne')
    erreur = fields.Char('Message')