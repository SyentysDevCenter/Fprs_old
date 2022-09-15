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
    'depends': ['base','ao','ao_pmo', 'ao_sdp', 'product', "sale", 'sales_team', 'project_sale'],
    'data': [
        'data/ao_product.xml',
        'views/sale_view.xml',
        'views/ao_views.xml',
    ],
    'installable': True,
    'application': False,
    'active': True
}