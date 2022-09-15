# -*- coding: utf-8 -*-
{
    'name': "Gestion des lignes de caution",

    'summary': """
        """,
    'description': """

    """,

    'author': "Andema",
    'website': 'http://www.andemaconsulting.com',
    'category': 'account',
    'version': '14.0',
    'depends': ['account',
                ],
    'data': [
        "security/caution_security.xml",
        "security/ir.model.access.csv",
        "views/bank_caution_views.xml",

             ],
    'installable': True,
    'application': False,
    'active': True
}
