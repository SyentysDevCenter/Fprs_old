# -*- coding: utf-8 -*-
{
    "name": "Field service extend",
    "version": "1.0",
    "category": "Operations/Field Service",
    "description": """ 
    Field service extend
    """,
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
  #  "depends": ['base','industry_fsm','sale', 'project_wbs', 'ao_sale'],
    "depends": ['base', 'sale', 'project_wbs','industry_fsm_extend'],

    "data": [
        'views/project_task_views.xml'
    ],
    'demo': [],
    "active": True,
    "installable": False,
    'application': False,
    'auto_install': False,
}