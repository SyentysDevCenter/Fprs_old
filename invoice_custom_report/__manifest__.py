# -*- coding: utf-8 -*-
{
    'name': "invoice_custom_report",

    'summary': """
        Invoice,sale,tasks and attachments """,



    'author': "Syentys",
    'website': "http://www.syentys.com",
    'category': 'Account',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account', 'sale_fsm_extend'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/partner_views.xml',
        'views/sale_views.xml',
        'views/invoice_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
