# -*- coding: utf-8 -*-
{
    'name': "import_contracts_assistant",

    'summary': """
        Import sale contracts Assistant""",


    'author': "Syentys",
    'website': "http://www.syentys.com",

    'version': '14.0.0.1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sales_contract', 'sale', 'project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_contracts_assistant.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
