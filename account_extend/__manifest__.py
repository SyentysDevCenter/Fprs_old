# -*- coding: utf-8 -*-
{
    'name': "account_extend",

    'summary': """
        Accounting Extension""",

    'author': "ANDEMA",
    'website': "http://www.andemaconsulting.com",
    'version': '0.11',
    'depends': ["base", "account", "account_accountant", "sale", "sale_fsm_extend",  'analytic',
                'sales_team', 'account_reports', 'partner_extend', 'sale_templates', 'subcontracting_invoice', 'project_group'],
    'data': [


        'security/security.xml',
        'security/ir.model.access.csv',
'wizard/update_invoice_line_account.xml',
        'data/followup_template.xml',
        'views/accounting_views.xml',
        'views/sales_views.xml',
        'views/partner_views.xml',
        'views/account_move_views.xml',
        'views/res_company.xml',
        'wizard/assistant_sous_traitant.xml',

    ],


    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
