# -*- coding: utf-8 -*-
{
    "name": "Project WBS",
    "version": "1.0",
    "category": "PMO",
    "description": """ 
   
    """,
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": ['base','project', 'analytic', 'portal', 'uom' ,'account_forecast', 'analytic_timesheet'],
    "data": [
        "views/project_views.xml",
        "views/wbs_view.xml",
        "views/task_views.xml",
        "views/analytic_line_views.xml",
        'security/pmo_security.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}