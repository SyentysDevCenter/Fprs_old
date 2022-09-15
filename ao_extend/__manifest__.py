# -*- coding: utf-8 -*-
{
    'name': "Gestion des appels d'offres- extension",

    'description': """
            Gestion des appels d'offre- extension

    """,

    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'category': 'Project',
    'version': '0.1',
    'depends': ['base',

                'ao',
                ],

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
    'active': True,
    'uninstall_hook': "uninstall_hook",

}