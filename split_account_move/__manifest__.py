# -*- coding: utf-8 -*-
{
    'name': "split account move line",

    'summary': """
        Accounting Extension""",

    'author': "ANDEMA",
    'website': "http://www.andemaconsulting.com",
    'version': '0.11',
    'depends': ["base", "account", ],
    'data': [

        #
        # 'security/security.xml',
        'security/ir.model.access.csv',
'wizard/split_wizard.xml',
'views/account_move_views.xml',


    ],


    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
