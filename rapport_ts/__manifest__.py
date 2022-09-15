# -*- coding: utf-8 -*-
{
    'name': "rapport_ts",

    'summary': """
        Rapport TS""",



    'author': "Syentys",
    'website': "http://www.syentys.odoo.com",
    'version': '14.0.0.1',
    'depends': ['base', 'project', 'hr_timesheet', 'analytic', 'hr', 'timesheet_grid'],
    'data': [
        'security/ir.model.access.csv',
        'views/task_views.xml',
        'views/employee_views.xml',
        'wizard/ts_report_wizard.xml',
        'report/paper.xml',
        'report/report_config.xml',
        'report/ts_report.xml',
    ],
    'demo': [
    ],
}
