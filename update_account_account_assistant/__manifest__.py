# -*- coding: utf-8 -*-
{
    'name': "update_account_account_assistant",

    'summary': """
       Update account move line Account """,

    'author': "Syentys",
    'website': "http://www.syentys.fr",
    'category': 'Account',
    'version': '14.0.0.1',

    'depends': ['base', 'account'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_move_line_views.xml',
        'wizard/update_account.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
