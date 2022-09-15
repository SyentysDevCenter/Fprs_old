from odoo import models, fields, api, _
import openpyxl
import base64
import io


class ImportDPGF(models.TransientModel):
    _name = 'import.dpgf'

    excel_file = fields.Binary('Fichier Excel')

    def import_data(self):
        file = base64.b64decode(self.excel_file)
        xls_filelike = io.BytesIO(file)
        wb = openpyxl.load_workbook(xls_filelike)
        ws_dpgf = wb.worksheets[0]
        ws_cost = wb.worksheets[1]

        wbs_root = self.env['project.wbs']
        wbs_cost_line = self.env['wbs.cost.line']
        wbs_cost_type = self.env['wbs.cost.type'].search([])
        uom_uom = self.env['uom.uom'].search([('active', '=', 'true')])

        type_data = {
            'F': ['Article', 'product.product', 'default_code'],
            'MO': ['Employé', 'hr.employee', 'name'],
        }
        type_list = {}
        for type in wbs_cost_type:
            type_list[type.model_id.name] = type.id

        uom_list = {}
        for uom in uom_uom:
            uom_list[uom.name] = uom.id

        data_dpgf = []
        for i, row in enumerate(ws_dpgf.rows):
            if i > 0:
                res_wbs = wbs_root.search(
                    [('code', '=', row[1].value), ('project_id', '=', self.env.context.get('active_id'))])
                if not res_wbs:
                    data_dpgf.append({'project_id': self.env.context.get('active_id'),
                                     'code_client': row[0].value,
                                     'code': row[1].value,
                                     'name': row[2].value,
                                     'unit_price': row[3].value,
                                     'uom_id': uom_list[row[4].value] if row[4].value in uom_list.keys() else False,
                                     'qty': row[5].value,
                                     'is_invoicable': False
                                      })
        wbs_root.create(data_dpgf)

        data_cost = []
        for i, row in enumerate(ws_cost.rows):
            if i > 0:
                product_id = self.env[type_data[row[1].value][1]].search([(type_data[row[1].value][2], '=', row[3].value)], limit=1)

                data_cost.append({'wbs_id': wbs_root.search([('code', '=', row[0].value)], limit=1).id,
                                 'reference': '%s,%s' % (type_data[row[1].value][1], product_id.id),
                                 'product_id': product_id.id if type_data[row[1].value][0] == 'Article' else False,
                                 'type_id': type_list[type_data[row[1].value][0]],
                                 'unit_cost': row[4].value,
                                 'uom_id': uom_list[row[5].value] if row[5].value in uom_list.keys() else False,
                                 'qty': row[6].value,
                                 'date': fields.Date.from_string(row[7].value)
                                  })
        wbs_cost_line.create(data_cost)
