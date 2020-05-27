# -*- coding: utf-8 -*-
{
    'name': "Custom Aged Payable Report",

    'summary': """
        This module personalize Aged Payable Report
    """,

    'description': """
        This module personalize Aged Payable Report
        Invoicing->Reportes->Partners Reports -> Aged Payable Report.
        
        Add Vendor Caegory Filter
        Add Currency Filter
        Change tag on column repor from "No debido en (Not due on)" —> "Al corriente"
        Change tag from "Viejo (Older)" —> "mas de 120 dias"
        
        If report is run only in one currency then it will display only movements
        posted only on that currency and in its original currency.
        
        If report is run in all currencies then native Odoo report will be displayed,
        all transactions converted to the company currency.
    """,

    'author': "Mayte Montano",
    'website': "http://www.eadminpro.com",

    'category': 'accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly 'website',
    'depends': ['account', 'account_reports'],

    # always loaded
    'data': [
        'views/search_template_view.xml',
    ],
}
