# -*- coding: utf-8 -*-
{
    "name": "Dépannage",
    "version": "1.3",
    "category": "Operations/Field Service",
    "description": """ 
    Field service extend
    """,
    'author': 'SYENTYS',
    'website': 'http://www.syentys.com',
  #  "depends": ['base','industry_fsm','sale', 'project_wbs', 'ao_sale'],
    "depends": ['base', 'sale', 'industry_fsm', 'timesheet_grid','web','web_enterprise', 'project_extend', 'mail',
                'sale_timesheet', 'project_sale', 'account', 'base_automation', 'sale_templates', 'hr', 'l10n_fr', 'sale_stock'],

    "data": [
        'security/fsm_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/fsm_task_views.xml',
        'views/sale_views.xml',
        'data/fsm_cron.xml',
        'data/corps_etat_data.xml',
        'views/template.xml',
        'views/hr_views.xml',
        'views/suivi_bc.xml',
        'views/corps_etat_views.xml',
        'report/layout.xml',
        'report/project_task_report.xml',
        'report/report_config.xml',
        'data/mail_data.xml',
    ],
    'css': ['static/src/css/page.css'],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}
