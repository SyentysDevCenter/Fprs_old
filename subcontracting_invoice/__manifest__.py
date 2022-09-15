# -*- coding: utf-8 -*-
{
    "name": "Facture de soutraitance",
    "version": "1.2",
    "category": "Invoices & Payments",
    "description": """ 
    AO / Projet.
    """,
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
    "depends": ['base','account', 'partner_extend', 'purchase'],
    "data": [
        # "security/ir.model.access.csv",
        # 'wizard/requisition_wizard_views.xml',
        # 'views/product_views.xml',
        'views/account_move.xml',
        'views/sous_traitant_menu.xml',

    ],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}