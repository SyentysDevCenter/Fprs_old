# -*- coding: utf-8 -*-
{
    'name': "opm_model_reports",

    'summary': """
        OPM Model reports""",
    'author': "Syentys",
    'website': "http://www.syentys.com",

    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account','account_extend', 'project_extend'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/layout.xml',
        'report/sale_order_report.xml',
        'report/report_config.xml',

        'report/invoice_report.xml',
        'report/meudon_invoice_report.xml',
        'views/sale_view.xml',
        'wizard/import_project_wizard.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
