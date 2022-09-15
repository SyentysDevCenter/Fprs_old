# -*- coding: utf-8 -*-
{
    'name': "WBS- extend",

    'description': """
            wbs- extension
    """,
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    'category': 'Project',
    'version': '0.1',
    'depends': ['base','project_wbs','ao_sdp'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/wbs_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/ao_demo.xml'
    ],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}
