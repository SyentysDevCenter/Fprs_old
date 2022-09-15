# -*- coding: utf-8 -*-

import odoorpc
import json
import openpyxl
from pathlib import PureWindowsPath as Path
import base64
import io

with open('connection.json.default') as connection_configuration_file:
    connection_configuration = json.load(connection_configuration_file)


path = Path(connection_configuration['path'])
filepath_articles = path / "product.xlsx"


target_odoo = odoorpc.ODOO(**connection_configuration['server'])
target_odoo.login(**connection_configuration['database'])
timeout_backup = target_odoo.config['timeout']
target_odoo.config['timeout'] = 2400  # 20 minutes

ProductTemplate = target_odoo.env['product.template']
ProductCategory = target_odoo.env['product.category']

category_by_level = dict()
category_by_apol_id = dict()


print('Loading ARTICLE1')
#
# file = open(filepath_articles, 'rb')
# xls_filelike = io.BytesIO(file)
wb = openpyxl.load_workbook(filepath_articles)
ws = wb.worksheets[0]
product_categ = ProductCategory.search_read([], ["id", "name"])
categ_list = {}
for categ in product_categ:
	print('categ', categ)
	categ_list[categ['name']] = categ['id']
products = []


for i, row in enumerate(ws.rows):
	if i > 1:
		products.append({'default_code': row[0].value,
						 'name': row[2].value,
						 'type': 'product',
						 'categ_id': categ_list[row[1].value],
						 'description_sale': row[3].value,
						 'list_price': row[4].value})
		print('pppppp', row[0].value)

# create the product template
create_ids = ProductTemplate.create(products)
print("prodcut.template: %d created" % len(create_ids))

target_odoo.config['timeout'] = timeout_backup
