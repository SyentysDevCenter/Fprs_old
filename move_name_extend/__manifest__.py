# -*- coding: utf-8 -*-
{
    'name': "Move name extend",

    'summary': """
        update the refund code""",
    'author': "Syentys",
    'website': "http://www.syentys.com",

    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',

    'views/account_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
