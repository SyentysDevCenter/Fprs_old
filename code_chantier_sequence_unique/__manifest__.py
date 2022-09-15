# -*- coding: utf-8 -*-
{
    'name': "code_chantier_sequence_unique",

    'summary': """""",

    'description': """""",

    'author': "Syentys",
    'website': "http://www.syentys.fr",

    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'menu_chantier'],

    # always loaded
    'data': [
        # data
        'data/sequence.xml',
        # views
        'views/project_extend.xml',
    ],
}
