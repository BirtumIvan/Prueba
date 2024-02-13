# -*- coding: utf-8 -*-
{
    'name': 'Prueba_cron',
    'version': '16.0.1.0.0',
    'description': """ Prueba_cron Description """,
    'summary': """ Prueba_cron Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    'data': [
        'data/ir_cron.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
    ],'assets': {
            'web.assets_backend': [
                'prueba_cron/static/src/**/*'
            ],
        },
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
