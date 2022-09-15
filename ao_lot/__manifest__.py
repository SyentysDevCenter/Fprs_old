# -*- coding: utf-8 -*-
{
    'name': "Appels d'offres avec LOT",
    'description': """
            Gestion des appels d'offre- Lot
    """,
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'category': 'Project',
    'version': '0.1',
    'depends': ['base', 'project_wbs', 'ao_pmo','ao',],
    'data': [
        'security/ir.model.access.csv',
        'views/ao_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/ao_demo.xml'
    ],
    'installable': True,
    'application': False,
    'active': True
}