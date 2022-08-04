# -*- encoding: utf-8 -*-
###############################################################################
#
#    Module Writen to Odoo14, Open Source Management Solution
#
############################################################################
{
    'name': 'Birtum | Internal Transfer',

    'summary': """Internal Transfer""",

    'description': """
        Internal Transfer
    """,

    'author': 'BIRTUM ©',

    "website": "https://www.birtum.com",

    'category': 'Extra Tools',

    'version': '14.0',

    'depends': [
        'base',
        'account',
        'account_accountant',
    ],

    'data': [
        'views/inherit_account_payment_views.xml',
              
    ],
    'installable': True,

    'active': False,

    'certificate': '',

    'application':False,
}