# -*- coding: utf-8 -*-
{
    'name': "Visites des lieux",

    'summary': """
        Gestion des différentes visites des lieux""",

    'description': """
       Gestion des visites des lieux :
    """,

    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'gestion de projet',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_automation'
                ],

    # always loaded
    'data': ['security/visite_security.xml',
             'security/ir.model.access.csv',
             'views/visite_view.xml',
             'data/visite_cron.xml'
    ],
    # only loaded in demonstration mode
    'demo': ['demo/demo.xml'
    ],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}