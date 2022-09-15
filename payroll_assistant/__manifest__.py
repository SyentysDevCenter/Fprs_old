# -*- coding: utf-8 -*-
{
    'name': "payroll_assistant",

    'summary': """
        Payroll assistant""",



    'author': "Syentys",
    'website': "http://www.syentys.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/payroll_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
