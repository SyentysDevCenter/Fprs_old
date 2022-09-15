# -*- coding: utf-8 -*-
{
    'name': "Coef DPFG",

    'summary': """
        Coefficient DPFG""",

    'description': """
        Add coefficient to project
    """,

    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',

    # for the full list
    'category': 'Project',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'ao_sdp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
