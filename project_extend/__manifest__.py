# -*- coding: utf-8 -*-
{
    "name": "Project extend",
    "version": "1.3",
    "category": "PMO",
    "description": """ 
   
    """,
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": ['base','project', 'hr_timesheet', 'account_forecast', 'purchase', 'stock', 'hr_expense','industry_fsm'],
    "data": [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/menu.xml',
        'views/vue.xml',
        'views/project_etat_views.xml',
        'views/account_analytic_line_views.xml',
        'wizard/update_conducteur_travaux_wizard_views.xml',

    ],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}