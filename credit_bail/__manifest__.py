# -*- coding: utf-8 -*-
{
    'name': "credit_bail",

    'summary': """""",

    'description': """""",

    'author': "Syentys",
    'website': "https://www.syentys.fr/",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account'],

    # always loaded
    'data': [
        # security
        'security/credit_bail_security.xml',
        'security/ir.model.access.csv',
        # data
        'data/cron.xml',
        # views
        'views/credit_bail.xml',
    ],
}
