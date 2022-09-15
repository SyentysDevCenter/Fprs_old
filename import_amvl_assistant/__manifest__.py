# -*- coding: utf-8 -*-
{
    'name': "import_amvl_assistant",

    'summary': """
        Import account move line assistant""",

    'author': "Syentys",
    'website': "http://www.syentys.com",
    'version': '14.0.0.1',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_move_views.xml',
        'views/account_account.xml',
        'wizard/import_amvl_wizard_views.xml',

    ],
    'demo': [
    ],
}
