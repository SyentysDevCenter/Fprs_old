# -*- coding: utf-8 -*-
{
    'name': "Partner grand livre",

    'summary': """
        """,
    'description': """

    """,

    'author': "Andema",
    'website': 'http://www.andemaconsulting.com',
    'category': 'account',
    'version': '10.0',
    'depends': ['base','account','account_reports'
                ],
    'data': [
        'security/ir.model.access.csv',

        'views/account_move.xml',
        'report/layout.xml',
        'report/partner_ledger.xml',
        'report/report_conf.xml',

        'wizard/partner_ledger_wizard.xml'



    ],
    'installable': True,
}
