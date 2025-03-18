# -*- coding: utf-8 -*-
{
    'name': 'DemostracionOdoo',
    'version': '1.0',
    'summary': 'Módulo de demo',
    'description': 'Modulo de demo y pruebas de practicas de Odoo',
    'author': 'Vicent Castells',
    'website': "https://github.com/VicentCastells6",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    
    
    
    # Icon
    'icon': '/Demostracion/static/description/icon.png',
}

