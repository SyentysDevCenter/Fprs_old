# -*- coding: utf-8 -*-
{
    "name": "Expense extend",
    "version": "1.0",
    "category": 'Human Resources/Expenses',
    "description": """ 
    Manage expenses by Employees
    """,
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
    "depends": ['base', 'hr_expense'],

    "data": [
        'views/hr_expense_views.xml',
        'views/hr_expense_report.xml',
    ],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}