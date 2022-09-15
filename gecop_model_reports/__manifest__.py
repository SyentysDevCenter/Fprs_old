# -*- coding: utf-8 -*-
{
    'name': "gecop_model_reports",

    'summary': """
        GCP Reports Models""",


    'author': "Syentys",
    'website': "http://www.syentys.com",

    'category': 'Sale',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account_extend', 'sale_fsm_extend', 'account', 'sale_report', 'report_qweb_element_page_visibility', 'gcp_externe'],

    # always loaded
    'data': [
        'report/report_config.xml',
        'report/report_layout.xml',
        'report/account/invoice_report_template.xml',
        'report/account/gecop_invoice_report.xml',
        'report/account/gecop_invoice_valophis_report.xml',
        'report/account/gecop_invoice_rivp_report.xml',
        'report/account/gecop_invoice_siret_report.xml',
        'report/account/gecop_invoice_oph_report.xml',
        'report/account/gecop_reha_invoice_report.xml',
        'report/account/gecop_invoice_sous_traitant.xml',

        'report/sale/sale_template.xml',
        'report/sale/sale_template_second.xml',
        'report/sale/bc_creteil_report_template.xml',
        'report/sale/sale_order_report.xml',
        'report/sale/sale_order_regul_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
