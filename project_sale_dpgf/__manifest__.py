# -*- coding: utf-8 -*-
{
    "name": "Project sale dpgf",
    "version": "1.0",
    "category": "PMO",
    "description": """ 
   
    """,
    'author': 'Andema',
    'website': 'http://www.andemaconsulting.com',
    "depends": ['base', 'project', 'project_wbs', 'project_sale','sale_fsm_extend','sale_templates','sale_report', 'gcp_externe'],
    "data": [
        'data/dpgf_sale_sequence.xml',
        'security/fsm_security.xml',
        'security/ir.model.access.csv',
        "views/project_views.xml",
        "views/sale_views.xml",
        "report/report_layout.xml",
        "report/sale_dpgf_report_template.xml",
        "report/paper_format.xml",
        "report/report_config.xml",

        # 'security/ir.model.access.csv'
    ],
    'demo': [],
    "active": True,
    "installable": True,
    'application': False,
    'auto_install': False,
}