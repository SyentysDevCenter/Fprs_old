# -*- coding: utf-8 -*-

import openpyxl
from odoo import models, fields, api, _
import base64
import io


class ImportProduct(models.TransientModel):
    _name = 'product.import.wizard'

    excel_file = fields.Binary('Fichier Excel')

    def import_data(self):
        file = base64.b64decode(self.excel_file)
        xls_filelike = io.BytesIO(file)
        wb = openpyxl.load_workbook(xls_filelike)
        ws = wb.worksheets[0]
        columns = ws.max_column
        product_template = self.env['product.template']
        product_categ = self.env['product.category'].search([])
        categ_list = {}
        for categ in product_categ:
            categ_list[categ.name] = categ.id
        products = []
        for i, row in enumerate(ws.rows):
            if i >0:
                products.append({'default_code': row[0].value,
                                         'name': row[2].value,
                                         'type': 'product',
                                         'categ_id': categ_list[row[1].value],
                                         'description_sale': row[3].value,
                                         'list_price': row[4].value})
                print('pppppp', row[0].value)
        product_template.create(products)


