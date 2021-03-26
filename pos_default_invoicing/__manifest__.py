# -*- coding: utf-8 -*-

{
    'name': 'Pos Default Invoicing',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'This module allows you set invoice button active by default.',
    'description': """

=======================

This module allows you set invoice button active by default.

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/views.xml',
        'views/templates.xml'
    ],
    'qweb': [
        # 'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/pos.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 19,
    'currency': 'EUR',
}
