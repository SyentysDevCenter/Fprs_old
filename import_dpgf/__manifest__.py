{
    'name': "Import DPGF",
    'version': "14.0.0.0",
    'depends': ['base', 'project', 'project_wbs'],
    'author': "ANDEMA",
    'website': 'http://www.andemaconulting.com',
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_dpgf_wizard.xml',
        'views/import_dpgf_views.xml',
    ],
    'installable': True,
    'application': False,
    'active': True
}
