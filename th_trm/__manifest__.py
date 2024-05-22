# -*- coding: utf-8 -*-
{
    'name': "ABS TRM",
    'summary': """ABS TRM""",
    'category': 'AUM Business System/ TRM',
    'description': """Functional group recruiting lecturers""",
    'author': "ABS",
    'website': "http://www.yourcompany.com",
    'version': '16.0.250324',
    'application': True,
    'depends': [
        'base',
        'mail',
        'th_setup_parameters',
        'web_domain_field',
        'product',
        'th_contact',

    ],
    'data': [
        'data/th_data_module.xml',
        'security/th_trm_lead_security.xml',
        'security/ir.model.access.csv',
        'data/code_name_data.xml',
        'views/th_trm_lead_view.xml',
        'views/th_trm_res_partner.xml',
        # 'views/th_trm_group_view.xml',
        'views/th_trm_stage_view.xml',
        'views/th_trm_team_view.xml',
        'views/th_trm_status_detail.xml',
        'views/th_trm_warehouse_view.xml',
        'views/th_lecturer_profile_view.xml',
        'views/th_trm_source_view.xml',
        'views/th_trm_channel_view.xml',
        'wizard/th_share_the_chance_view.xml',
        'wizard/trm_import_view_wizard.xml',
        'views/th_menu_trm.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'license': 'LGPL-3',
}
