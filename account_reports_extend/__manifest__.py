# -*- coding: utf-8 -*-
{
    'name': "Print partner ledger unfolded",

    'summary': """
       Print partner ledger unfolded""",

    'author': "ANDEMA",
    'website': "http://www.andemaconsulting.com",
    'version': '0.11',
    'depends': ["base", "account", "account_reports",],
    'data': [
'views/partner_ledger_template.xml'

    ],


    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
