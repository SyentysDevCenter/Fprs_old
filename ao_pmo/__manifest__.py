# -*- coding: utf-8 -*-
{
    "name": "AO / Projet",
    "version": "1.0",
    "category": "PMO",
    "description": """ 
    AO / Projet.
    """,
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
    "depends": ['base','ao', 'project_wbs', 'hr_timesheet'],
    "data": [
        "views/ao.xml",
        "views/project.xml",
        'security/ir.model.access.csv'
    ],
    'demo': [],
    "active": True,
    "installable": True,
    'applcation': False,
    'auto_install': False,
}