# -*- coding: utf-8 -*-
{
    'name': "Generation du devis des AO",
    'description': """
        Generation du devis à partir des AO
    """,
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'category': 'Project',
    'version': '0.1',
    'depends': ['base', "sale", 'sales_team', 'mail', "product"],
    'data': [
        'views/sale_view.xml',
    ],
    'installable': True,
    'application': False,
    'active': True
}