# -*- coding: utf-8 -*-
{
    'name': "project_group",
    'summary': """
        Groupes de chantier""",
    'author': "ANDEMA",
    'website': "http://www.andemaconsulting.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','sale','project','hr_timesheet','sale_fsm_extend','project_extend'],
    'data': [
        'security/security.xml',

        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/sale_views.xml',
        'views/task_views.xml',

    ],
}
