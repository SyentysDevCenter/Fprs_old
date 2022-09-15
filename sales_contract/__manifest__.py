# -*- coding: utf-8 -*-
{
    'name': "Sales contracts",

    'summary': """
        """,

    'description': """
    Inventory
    """,
    'author': "SYENTYS",
    'website': "http://www.syentys.com",


    'version': '14.0.0.1',
    
    'depends': [
        'base','account', 'sale','product', 'mail', 'project', 'project_sale'


    ],

    'data': [
        'data/sequence.xml',
        'security/sales_contrat_security.xml',
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/sale_contract_views.xml',
        'views/partner_views.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
        'wizard/actualisation_prix.xml',

    ],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}
