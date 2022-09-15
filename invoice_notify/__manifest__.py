# -*- coding: utf-8 -*-
{
    "name": "Invoice Notify",

    "summary": """
        Invoice Notify""",

    "author": "ANDEMA",
    "website": "http://www.andemaconsulting.com",
    "category": "Uncategorized",
    "version": "0.1",
    "depends": ["base","account", "account_extend"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/facture_attente_views.xml",
        "data/activity.xml",
        "data/email_template.xml",

    ],
    "demo": [
    ],
}
