# -*- coding: utf-8 -*-
{
    'name': "Gestion des appels d'offres",

    'description': """
            Gestion des appels d'offre

    """,

    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'category': 'Project',
    'version': '0.1',
    'depends': ['base',
                'mail',
                'visite_lieux', 'bank_caution',
                'account',
                'hr','product','uom'],

    'data': [
          'wizard/refus_wizard.xml',

        'security/ao_security.xml',
        'security/ir.model.access.csv',
        'views/ao_views.xml',
        'views/dossier_views.xml',
        'data/ao_data.xml',
        'data/mail_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/ao_demo.xml'
    ],
    'installable': True,
    'application': False,
    'active': True
}