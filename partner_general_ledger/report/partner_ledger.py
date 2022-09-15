# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ReportPartnerLedger(models.AbstractModel):
    _name = 'report.partner_general_ledger.report_partnerledger'

    @api.model
    def _get_report_values(self, docids, data=None):
        partners = data.get('ids',[])
        company = self.env['res.company'].browse(data['company_id'])
        data['company_id'] = company
        data['currency'] = company.currency_id.name
        if data['all_partners']:
            partner_ids = self.env['res.partner'].search(['|',('active', '=', True), (('active', '=', False))])
            print('partner_ids', partner_ids)
        elif partners:
            partner_ids = self.env['res.partner'].browse(data['ids'])
            # data['partner_names'] = ','.join(partner_ids.mapped('name'))

            # data['partner_names'] = ','.join(partner_ids.mapped('name'))
        if partner_ids:
            # print('partner_idss', partner_ids)
            data['lines'] = []
            query = """SELECT l.partner_id, a.id, a.move_type, a.journal_id, j.type as journal_type, j.code, a.ref, a.name, a.move_type, a.date, a.amount_total,sum(l.credit) as credit,sum(l.debit) as debit, l.account_id, ac.code as account_code, 
                                                       sum(t10.tax) as partner_total_10,
                                                       sum(t20.tax) as partner_total_20,
                                                       sum(t55.tax) as partner_total_55,
                                                       sum(t7.tax) as partner_total_7,
                                                       sum(t196.tax) as partner_total_196,
                                                       sum(t0.tax) as partner_total_0

                                                       FROM account_move_line l
                                                       LEFT JOIN  account_move a ON a.id = l.move_id
                                                       LEFT JOIN  account_account ac ON ac.id = l.account_id 
                           							LEFT JOIN account_journal j ON j.id = a.journal_id
                           							LEFT JOIN account_move_tax_line t10 ON  t10.move_id = a.id AND t10.tax_amount = 10.00
                           							LEFT JOIN account_move_tax_line t20 ON t20.move_id = a.id AND t20.tax_amount = 20.00
                           							LEFT JOIN account_move_tax_line t55 ON t55.move_id = a.id AND t55.tax_amount = 5.50
                           							LEFT JOIN account_move_tax_line t7 ON t7.move_id = a.id AND t7.tax_amount = 7.00
                           							LEFT JOIN account_move_tax_line t196 ON t196.move_id = a.id AND t196.tax_amount = 19.60
                           							LEFT JOIN account_move_tax_line t0 ON t0.move_id = a.id AND t0.tax_amount = 0.00
                                                       WHERE  
                                                        a.state = 'posted'  and l.full_reconcile_id is null  and  ac.internal_type = 'receivable'                          

                                                       """

            if len(partner_ids)== 1:
               query +=""" and l.partner_id = %s"""
               params = [partner_ids[0].id]
            else:
               query +=""" and l.partner_id in %s"""
               params = [tuple(partner_ids.mapped('id'))]

            if data['date_from']:
                query += """ and 
                                          a.date >=%s"""
                params.append(data['date_from'])
            if data['date_to']:
                query += """ 
                                         and a.date <= %s """
                params.append(data['date_to'])

            query += """ GROUP BY a.journal_id, a.id ,j.type, j.code,   a.ref, a.name, a.move_type, a.date, a.id, l.account_id , l.partner_id , ac.code , a.move_type 
                                       ORDER BY l.partner_id, a.date"""
            self._cr.execute(query, tuple(params))
            lines = self._cr.dictfetchall()
            print('lineslines', lines)
            new_dict = {item['partner_id']: [l for l in lines if l['partner_id']== item['partner_id']] for item in lines}
            print('new_dict', new_dict)
            data['partner_total_credit_global'] = 0
            data['partner_total_debit_global'] = 0
            data['partner_total_10_global'] = 0
            data['partner_total_20_global'] = 0
            data['partner_total_55_global'] = 0
            data['partner_total_7_global'] = 0
            data['partner_total_196_global'] = 0
            data['partner_total_EXO_global'] = 0
            data['partner_total_CUMUL_global'] = 0

            for partner in new_dict:
                partner_id = self.env['res.partner'].browse(partner)
                partner_total_credit = 0
                partner_total_debit = 0
                partner_total_10 = 0
                partner_total_20 = 0
                partner_total_55 = 0
                partner_total_7 = 0
                partner_total_196 = 0
                partner_total_EXO = 0
                partner_total_CUMUL = 0

                # query = """SELECT a.id, a.journal_id, j.type as journal_type, j.code, a.ref, a.name, a.move_type, a.date, a.amount_total,
                #             sum(t10.tax) as partner_total_10,
                #             sum(t20.tax) as partner_total_20,
                #             sum(t55.tax) as partner_total_55,
                #             sum(t7.tax) as partner_total_7,
                #             sum(t196.tax) as partner_total_196,
                #             sum(t0.tax) as partner_total_0
                #
                #             FROM account_move a
				# 			LEFT JOIN account_journal j ON j.id = a.journal_id
				# 			LEFT JOIN account_move_tax_line t10 ON  t10.move_id = a.id AND t10.tax_amount = 10.00
				# 			LEFT JOIN account_move_tax_line t20 ON t20.move_id = a.id AND t20.tax_amount = 20.00
				# 			LEFT JOIN account_move_tax_line t55 ON t55.move_id = a.id AND t55.tax_amount = 5.50
				# 			LEFT JOIN account_move_tax_line t7 ON t7.move_id = a.id AND t7.tax_amount = 7.00
				# 			LEFT JOIN account_move_tax_line t196 ON t196.move_id = a.id AND t196.tax_amount = 19.60
				# 			LEFT JOIN account_move_tax_line t0 ON t0.move_id = a.id AND t0.tax_amount = 0.00
                #             WHERE
                #              a.state = 'posted'  and a.partner_id = %s and a.move_type in ('out_invoice', 'out_refund') and a.payment_state ='not_paid'
                #
                #             """

                # print('linnnnnnnnn', lines)
                if new_dict[partner]:
                    partner_lines = {'account'             : partner_id.property_account_receivable_id.code,
                                     'partner_name'        : partner_id.name,
                                     'partner_total_credit': partner_total_credit,
                                     'partner_total_debit' : partner_total_debit,
                                     'partner_total_10'    : partner_total_10,
                                     'partner_total_20'    : partner_total_20,
                                     'partner_total_55'    : partner_total_55,
                                     'partner_total_7'     : partner_total_7,
                                     'partner_total_196'   : partner_total_196,
                                     'partner_total_EXO'   : partner_total_EXO,
                                     'partner_total_CUMUL' : partner_total_CUMUL,
                                     'partner_lines'       : []
                                     }
                    for aml in new_dict[partner]:

                        # print('aml', aml)
                        line_to_append = aml
                        if aml['move_type'] in ('out_refund', 'in_invoice'):
                            partner_lines['partner_total_10'] -= aml['partner_total_10'] or 0
                            partner_lines['partner_total_20'] -= aml['partner_total_20'] or 0
                            partner_lines['partner_total_55'] -= aml['partner_total_55'] or 0
                            partner_lines['partner_total_7'] -= aml['partner_total_7'] or 0
                            partner_lines['partner_total_196'] -= aml['partner_total_196'] or 0
                            partner_lines['partner_total_EXO'] -= aml['partner_total_0'] or 0
                        else:
                            partner_lines['partner_total_10'] += aml['partner_total_10'] or 0
                            partner_lines['partner_total_20'] += aml['partner_total_20'] or 0
                            partner_lines['partner_total_55'] += aml['partner_total_55'] or 0
                            partner_lines['partner_total_7'] += aml['partner_total_7'] or 0
                            partner_lines['partner_total_196'] += aml['partner_total_196'] or 0
                            partner_lines['partner_total_EXO'] += aml['partner_total_0'] or 0
                        ref = ''
                        if aml['name'] != None:
                            ref= aml['name']
                        line_to_append['debit'] = aml['debit']
                        line_to_append['account_id'] = aml['account_code']
                        line_to_append['credit'] = aml['credit']
                        line_to_append['amount_signed'] = aml['debit'] - aml['credit']
                        if aml['move_type'] in ('out_refund', 'in_invoice'):
                            line_to_append['partner_total_10'] =  (-1)* (aml['partner_total_10'] or 0.0)
                            line_to_append['partner_total_20'] =  (-1)* (aml['partner_total_20'] or 0.0)
                            line_to_append['partner_total_55'] =  (-1)* (aml['partner_total_55'] or 0.0)
                            line_to_append['partner_total_7'] =  (-1)* (aml['partner_total_7'] or 0.0)
                            line_to_append['partner_total_196'] =  (-1)* (aml['partner_total_196'] or 0.0)
                            line_to_append['partner_total_0'] =  (-1)* (aml['partner_total_0'] or 0.0)

                        partner_lines['partner_total_debit'] += aml['debit']
                        partner_lines['partner_total_credit'] += aml['credit']

                        if aml['move_type'] == 'out_invoice':
                            line_to_append['libelle'] = 'Facture '+ ref + ' '+( partner_id.name or '')

                        elif aml['move_type'] == 'out_refund':
                            line_to_append['libelle'] = 'Avoir '+ ref + ' '+ partner_id.name

                        elif aml['move_type'] == 'entry' and aml['journal_type'] in ('bank', 'cash'):
                            line_to_append['libelle'] = 'Paiement '+ ref  + ' '+ partner_id.name
                        else:
                            line_to_append['libelle'] = ref  + ' '+ partner_id.name

                        partner_lines['partner_lines'].append(line_to_append)



                    # print('partner_lines', partner_lines)
                    data['lines'].append(partner_lines)
                    data['partner_total_credit_global'] += partner_lines['partner_total_credit']
                    data['partner_total_debit_global'] += partner_lines['partner_total_debit']
                    data['partner_total_10_global'] += partner_lines['partner_total_10']
                    data['partner_total_20_global'] += partner_lines['partner_total_20']
                    data['partner_total_55_global'] += partner_lines['partner_total_55']
                    data['partner_total_7_global'] += partner_lines['partner_total_7']
                    data['partner_total_196_global'] += partner_lines['partner_total_196']
                    data['partner_total_EXO_global'] += partner_lines['partner_total_EXO']

        # print('dddddddddd2', data['lines'])

        return {
            'doc_ids'  : data['ids'],
            'doc_model': data['model'],
            'docs'     : docids,
            'data'     : data,
        }

