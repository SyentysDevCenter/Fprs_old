# -*- coding: utf-8 -*-
{
    "name": "Sous traitance",
    "version": "1.0",
    "category": "PMO",
    "description": """ 
    AO / Projet.
    """,
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
    "depends": ['base','sale', 'product', 'purchase', 'purchase_requisition'],
    "data": [
        "security/ir.model.access.csv",
        'wizard/requisition_wizard_views.xml',
        'views/product_views.xml',
        'views/sale_views.xml',

    ],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}