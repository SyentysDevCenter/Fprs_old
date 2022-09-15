# -*- coding: utf-8 -*-
{
    'name': "facturation_chorus",
    'summary': """
        Facturation Chorus""",

    'author': "ANDEMA",
    'website': "http://www.andemaconsulting.com",
    'category': 'Accounting',
    'version': '14.0.0.2',
    'depends': ['base','account','account_extend', 'invoice_custom_report'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/account_move_views.xml',
        'views/res_company_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': False,
    'active': True
}
