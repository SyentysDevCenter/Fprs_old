# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import io
import openpyxl


class ImportContractWizard(models.TransientModel):
    _name = 'import.contract.wizard'
    _description = 'Import sale contracts assistant'

    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    chantier_id = fields.Many2one('project.project', string='Chantier', required=True)
    excel_file = fields.Binary('Fichier Excel')
    type = fields.Selection([('maj','MISE À JOUR'),('cr','CRÉATION')], string="Type d'opération", required=True, default='cr')
    date_start = fields.Date('Date de début')
    date_end = fields.Date('Date de fin')
    erreur_ids = fields.One2many('import.contract.wizard.line', 'wizard_id', 'Erreurs')

    def valider(self):

        if not self.excel_file:
            raise ValidationError('Veuillez insérer un fichier Excel')
        else:
            Sale_contract = self.env['sale.contract']
            Sale_contract_line = self.env['sale.contract.line']
            Product_template = self.env['product.template']
            Udm_udm = self.env['uom.uom']
            file = base64.b64decode(self.excel_file)
            xls_filelike = io.BytesIO(file)
            udm_ids = Udm_udm.search([])
            wb = openpyxl.load_workbook(xls_filelike)
            ws = wb.worksheets[0]


            if self.type == 'maj':

                sale_contract = Sale_contract.search([('customer_id', '=', self.partner_id.id),('chantier_id', '=', self.chantier_id.id)])
                if not sale_contract:
                    raise ValidationError(
                        "Contrat introuvable pour le client %s et le chantier %s !" % (self.partner_id.name,self.chantier_id.name))
                else:
                    old = {}
                    for line in sale_contract.line_ids:
                        old[line.product_id.default_code] = line.price


                    for i, row in enumerate(ws.rows):
                        detail_product = str(row[0].value)
                        detail_product_name = str(row[1].value)
                        detail_prix_or_remise = str(row[2].value)
                        detail_type = str(row[3].value)
                        detail_udm = str(row[4].value)
                        if i > 0:
                            if detail_product != 'None':
                                old_product_line = sale_contract.line_ids.filtered(lambda u:  u.product_id.default_code and u.product_id.default_code.strip() == detail_product.strip())
                                if old_product_line:

                                    if detail_type != 'None':
                                        if detail_type.strip().lower() == 'prix':
                                            old_product_line.write({'type': 'price'})
                                            if detail_prix_or_remise != 'None':
                                                old_product_line.write({'price' : float(detail_prix_or_remise)})

                                        elif detail_type.strip().lower() == 'remise':
                                            old_product_line.write({'type': 'discount'})
                                            if detail_prix_or_remise != 'None':
                                                old_product_line.write({'discount' : float(detail_prix_or_remise)})

                                        else:
                                            old_product_line.write({'type': False})
                                            if detail_prix_or_remise != 'None':
                                                old_product_line.write({'price' : float(detail_prix_or_remise)})

                                    if detail_udm != 'None':
                                        udm_id = Udm_udm.search([('name', 'ilike', detail_udm)])
                                        if udm_id:
                                            old_product_line.product_uom_id = udm_id[0].id
                                        else:
                                            self.write({'erreur_ids': [(0, 0, {'ligne': i + 1,
                                                                               'erreur': "vérifier l'unite de mesure",
                                                                               })]})
                                else:
                                    create_line = {}
                                    create_line['contract_id'] = sale_contract.id
                                    if detail_product_name != 'None':
                                        existing_product = Product_template.search([('default_code', '=', detail_product.strip())])
                                        if not existing_product:
                                            cr_product = Product_template.create({'name': str(detail_product_name),
                                                                             'default_code': detail_product
                                                                             })
                                        else:
                                            cr_product = existing_product[0]
                                        if cr_product:
                                            create_line['product_id'] = cr_product.id

                                    if detail_type != 'None':
                                        if detail_type.strip().lower() == 'prix':
                                            create_line['type'] = 'price'
                                            if detail_prix_or_remise != 'None':
                                                create_line['price'] = float(detail_prix_or_remise)

                                        elif detail_type.strip().lower() == 'remise':
                                            create_line['type'] = 'discount'
                                            if detail_prix_or_remise != 'None':
                                                create_line['discount'] = float(detail_prix_or_remise)

                                        else:
                                            create_line['type'] = 'discount'
                                            if detail_prix_or_remise != 'None':
                                                create_line['price'] = float(detail_prix_or_remise)

                                    if detail_udm != 'None':

                                        udm_id = udm_ids.filtered(lambda u: u.name.strip().lower() == detail_udm.strip().lower())
                                        if udm_id:
                                            create_line['product_uom_id'] = udm_id[0].id
                                        else:
                                            self.write({'erreur_ids': [(0, 0, {'ligne': i + 1,
                                                                               'erreur': "vérifier l'Unité de mesure",
                                                                               })]})

                                    line = Sale_contract_line.create(create_line)
                    if sale_contract and not self.erreur_ids:
                        message = 'Mise à jour de contrat numéro  ' + str(sale_contract.name) + '<ul>'
                        for contract_line in sale_contract.line_ids:
                            message = message + '<li>[' + str(contract_line.product_id.default_code) + ']' + str(
                                contract_line.product_id.name)
                            if contract_line.product_id.default_code in old.keys():
                            # if old[contract_line.product_id.default_code]:
                                message = message + ' : ' + str(round(old[contract_line.product_id.default_code], 2)) + ' &rarr; '
                                message = message + str(round(contract_line.price, 2)) + '</li>'
                            else:
                                message = message + ' : ' + str(round(contract_line.price, 2))

                        message = message + '</ul>'
                        sale_contract.message_post(body=message)
                        return { 'type': 'ir.actions.act_window',
                                'name': 'Contrat mis à jour',
                                'res_model': 'sale.contract',
                                'res_id': sale_contract.id,
                                'view_type': 'form',
                                'view_mode': 'form',
                                'target': 'current',}


            if self.type == 'cr':
                if self.date_start > self.date_end:
                    raise ValidationError("Date début doit être antérieure à la date de fin!")

                sale_contracts = Sale_contract.search([('chantier_id', '=', self.chantier_id.id)])
                if sale_contracts:
                    raise ValidationError("Il exite un autre contrat lié à ce chantier")
                else:
                    data = {}
                    if self.chantier_id:
                        data['chantier_id'] = self.chantier_id.id
                    if self.partner_id:
                        data['customer_id'] = self.partner_id.id
                    data['date_start'] = self.date_start
                    data['date_end'] = self.date_end
                    create_contract = Sale_contract.create(data)

                    for i, row in enumerate(ws.rows):
                        detail_product = str(row[0].value)
                        detail_product_name = str(row[1].value)
                        detail_prix_or_remise = str(row[2].value)
                        detail_type = str(row[3].value)
                        detail_udm = str(row[4].value)
                        if i > 0:
                            line_data = {}
                            if create_contract:
                                line_data['contract_id'] = create_contract.id
                            if detail_product != 'None':
                                product = Product_template.search([('default_code', '=', str(detail_product.strip()))])
                                if product:
                                    line_data['product_id'] = product[0].id
                                else:
                                    if detail_product_name != 'None':
                                        cr_product = Product_template.create({'name': str(detail_product_name),
                                                                             'default_code': detail_product
                                                                             })
                                        if cr_product:
                                            line_data['product_id'] = cr_product.id

                                if detail_type != 'None' :

                                    if detail_type.strip().lower() == 'prix':
                                        line_data.update({'type': 'price'})
                                        if detail_prix_or_remise != 'None':
                                            line_data['price'] = float(detail_prix_or_remise)

                                    elif detail_type.strip().lower() == 'remise':
                                        line_data.update({'type': 'discount'})
                                        if detail_prix_or_remise != 'None':
                                            line_data['discount'] = float(detail_prix_or_remise)

                                    else:
                                        # line_data.update({'type': False})
                                        if detail_prix_or_remise != 'None':
                                            line_data.update({'type': 'price'})

                                            line_data['price'] = float(detail_prix_or_remise)

                                if detail_udm != 'None':
                                    udm_id = udm_ids.filtered(lambda u: u.name.strip().lower() == detail_udm.strip().lower())
                                    if udm_id:
                                        line_data['product_uom_id'] = udm_id[0].id
                                    else:
                                        self.write({'erreur_ids': [(0, 0, {'ligne': i + 1,
                                                                           'erreur': "vérifier l'unite de mesure",
                                                                           })]})

                                line = Sale_contract_line.create(line_data)
                    if create_contract:
                        message = 'Création de contrat numéro  ' + str(create_contract.name) + '<ul>'
                        for contract_line in create_contract.line_ids:
                            message = message + '<li>[' + str(contract_line.product_id.default_code) + ']' + str(
                                contract_line.product_id.name) + ' : ' + str(round(contract_line.price, 2))
                        message = message + '</ul>'
                        create_contract.message_post(body=message)
                        create_contract.Validate_contract()

        if self.erreur_ids:
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.contract.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            return { 'type': 'ir.actions.act_window',
            'name': 'Contrat mis à jour',
            'res_model': 'sale.contract',
            'res_id': create_contract.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',}



class ImportContractWizardLine(models.TransientModel):
    _name = 'import.contract.wizard.line'

    wizard_id = fields.Many2one('import.contract.wizard')
    ligne = fields.Char('Ligne')
    erreur = fields.Char('Erreur')