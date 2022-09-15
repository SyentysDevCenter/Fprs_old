# -*- coding: utf-8 -*-
{
    'name': "sale_order_report",
    'summary': """
        Sale Order Report""",
    'description': """
        Long description of module's purpose
    """,
    'author': "ANDEMA",
    'website': "http://www.andemaconsulting.com",
    'version': '0.2',
    'depends': ['base','sale','sale_templates','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/modalite_payment_views.xml',
        'views/partner_views.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
