# -*- coding: utf-8 -*-
{
    'name': 'DemostracionOdoo',
    'version': '1.0',
    'summary': 'Módulo de préstamo de equipos',
    'description': 'Este módulo permitirá a una empresa gestionar el préstamo de equipos (como portátiles, teléfonos, herramientas, etc.) a sus empleados.',
    'author': 'Vicent Castells',
    'website': "https://github.com/VicentCastells6",

    'category': 'Customizations',
    'depends': ['base', 'web', 'stock'],

    "data": [
        "security/ir.model.access.csv",
        "views/equipos.xml",
        "views/prestamos.xml",
    ],
    
    'assets': {
        'web.assets_backend': [
        ],
    },

    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
    'license': 'LGPL-3',

    'icon': '/Demostracion/static/description/icon.png',
}
