# -*- coding: utf-8 -*-
{
    'name': "account_followup_extend",

    'summary': """
        Accounting Extension""",

    'author': "ANDEMA",
    'website': "http://www.andemaconsulting.com",
    'version': '0.10',
    'depends': ["base", "account", 'account_followup'],
    'data': [
        'views/assets.xml',
        'views/account_move_view.xml'

    ],

    'qweb': ['static/xml/customer_statement.xml'],

    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
