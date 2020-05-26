# -*- coding: utf-8 -*-
{
    'name': "Sale Order Email Template",

    'summary': """
       Sale Order Email Template""",

    'description': """
       Sale Order Email Template
    """,

    'author': "Mayte Montano",

    'category': 'tools',
    'version': '1.0',

    'depends': ['sale', 'mail'],

    # always loaded
    'data': [
         'data/mail_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
