# -*- coding: utf-8 -*-

import openpyxl
from odoo import models, fields, api, _
import base64
import io
from odoo.exceptions import ValidationError
from datetime import datetime


class ImportProjectWizard(models.TransientModel):
    _name = 'import.project.wizard'
    _description = 'Importer les projets'

    excel_file = fields.Binary('Fichier Excel')
    erreur_ids = fields.One2many('import.project.wizard.erreur', 'maj_id', 'Erreurs')

    def import_data(self):

        if self.erreur_ids:
            for r in self.erreur_ids:
                r.unlink()


        file = base64.b64decode(self.excel_file)
        xls_filelike = io.BytesIO(file)
        wb = openpyxl.load_workbook(xls_filelike)
        ws = wb.worksheets[0]
        res_partner = self.env['res.partner'].sudo()
        project_project = self.env['project.project'].sudo()
        project_etat = self.env['project.etat'].sudo()

        for i, row in enumerate(ws.rows):
            numero_marche_projet = str(row[0].value)
            nom_projet = str(row[1].value)
            client_projet = str(row[2].value)
            description_projet = str(row[3].value)
            date_debut_projet = str(row[4].value)
            adresse_projet = str(row[5].value)
            code_postal_projet = str(row[6].value)
            ville_projet = str(row[7].value)
            etat_projet = str(row[8].value)

            if i > 0:
                project_vals = {}
                if str(date_debut_projet) != None:
                    project_vals['date_start'] = datetime.strptime(date_debut_projet, '%Y-%m-%d %H:%M:%S').date()
                project_vals['description'] = description_projet
                project_vals['name'] = nom_projet
                project_vals['numero_marche'] = numero_marche_projet
                project_vals['adresse_chantier'] = adresse_projet
                project_vals['code_postal_chantier'] = code_postal_projet
                project_vals['ville_chantier'] = ville_projet

                if etat_projet != None:
                    etat = project_etat.search([('name', 'ilike', etat_projet)])
                    if not etat:
                        self.write({'erreur_ids': [(0, 0, {'ligne': i + 1,
                                                           'erreur': "l'état de chantier n'a pas été trouvé sur la base de données"})]})
                    else:
                        project_vals['etat_chantier_id'] = etat[0].id

                if client_projet != None:
                    partner = res_partner.search([('name', 'ilike', client_projet)])
                    if not partner:
                        self.write({'erreur_ids': [(0, 0, {'ligne': i + 1,
                                                           'erreur': "le client n'a pas été trouvé sur la base de données"})]})
                    else:
                        project_vals['partner_id'] = partner[0].id
                # Projet  Create

                project_create = project_project.create(project_vals)

        if self.erreur_ids:
            return {
                'context': self.env.context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'import.project.wizard',
                'res_id': self.id,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        else:
            return {'type': 'ir.actions.act_window_close'}

    def test_data(self):

        if self.erreur_ids:
            for r in self.erreur_ids:
                r.unlink()

        file = base64.b64decode(self.excel_file)
        xls_filelike = io.BytesIO(file)
        wb = openpyxl.load_workbook(xls_filelike)
        ws = wb.worksheets[0]
        res_partner = self.env['res.partner'].sudo()
        project_etat = self.env['project.etat'].sudo()


        for i, row in enumerate(ws.rows):
            client_projet = str(row[2].value)
            etat_projet = str(row[8].value)

            if i > 0:

                if client_projet != None:
                    partner = res_partner.search([('name', 'ilike', client_projet)])
                    if not partner:
                        self.write({'erreur_ids': [(0, 0, {'ligne': i + 1,
                                                           'erreur': "le client n'a pas été trouvé sur la base de données"})]})
                if etat_projet != None:
                    etat = project_etat.search([('name', 'ilike', etat_projet)])
                    if not etat:
                        self.write({'erreur_ids': [(0, 0, {'ligne': i + 1,
                                                           'erreur': "l'état de chantier n'a pas été trouvé sur la base de données"})]})


        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'import.project.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


    def clear_data(self):
        if self.erreur_ids:
            for r in self.erreur_ids:
                r.unlink()
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'import.project.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

class ImportProjectWizardErreur(models.TransientModel):
    _name = 'import.project.wizard.erreur'

    maj_id = fields.Many2one('import.project.wizard')
    ligne = fields.Char('Ligne')
    erreur = fields.Char('Erreur')

