# -*- coding: utf-8 -*-
{
    'name': "Import Data For Inventory",

    'summary': """
        This module helps to upload data using an excel file for shipements & Receipts""",

    'description': """
        Upload data using an excel file 
    """,

    'author': "Noura JAMAL",
    'website': "https://www.linkedin.com/in/noura-jamal-1b846b1b8/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_picking_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True
}
