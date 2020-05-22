# -*- coding: utf-8 -*-
{
    'name': "Add Custom Button to Tree View",

    'summary': """
        Add button to Tree view and register new action for it
        """,

    'description': """
        Add button to Tree view and register new action for it.
        
        Usage:
        
        add js_class="sale_order_tree_view_button" in the tree node
        
        Odoo v13.0
    """,

    'author': "Mayte Montano",
    'website': "http://www.eadminpro.com/",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['sale'],
    
    'data': [
        'views/assets.xml',
        'views/sale_views.xml',        
    ],
    'qweb': [
        'static/src/xml/tree_view_button.xml',
    ],
    'auto_install' : True,
}
