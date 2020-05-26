# -*- coding: utf-8 -*-
{
    'name': "Fleet Insurance",

    'summary': """
       Fleet Insurance""",

    'description': """
Fleet Insurance
===============
This module allows administration of insurance policies for car fleets

    """,

    'author': "Mayte Montano",
    'website': "http://www.eadminpro.com",

    'category': 'Fleet',
    'version': '1.0',

    # any module necessary for this one to work correctly 
    'depends': ['fleet', 'base', 'mail'],

    # always loaded
    'data': [
         'views/fleet_vehicle_insurance_views.xml',
         'views/fleet_vehicle_views.xml',
         'data/fleet_insurance_data.xml',
         'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
