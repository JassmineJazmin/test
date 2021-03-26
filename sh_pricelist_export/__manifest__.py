
# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Export Pricelist",
    "author" : "Softhealer Technologies",
    "support": "support@softhealer.com",
    "website": "https://www.softhealer.com",
    "category": "Extra Tools",
    "summary": """This module will provide feature to export a pricelist customer wise. You can get multiple customers pricelist in single PDF as well as in excel file(with different sheet).
 Export Pricelist Odoo
 Export Customer Wise Pricelist Module, Multiple Customer Pricelist, Multi Pricelist In PDF, More Client Pricelist In Excel, Send Customer Pricelist Odoo.
Export Customer Pricelist Module, Multiple Customer Pricelist App, PDF Multi Pricelist Application, Client Pricelist In Excel, Send Customer Pricelist Odoo.

""",
    "description": """This module will provide feature to export a pricelist customer wise. You can get multiple customers pricelist in single PDF as well as in excel file(with different sheet).
 Export Pricelist Odoo
 Export Customer Wise Pricelist Module, Multiple Customer Pricelist, Multi Pricelist In PDF, More Client Pricelist In Excel, Send Customer Pricelist Odoo.
Export Customer Pricelist Module, Multiple Customer Pricelist App, PDF Multi Pricelist Application, Client Pricelist In Excel, Send Customer Pricelist Odoo.

""",    
    "version":"13.0.1",
    "depends" : ["base","sale_management","contacts"],
    "data" : [
              'security/ir.model.access.csv',
              'views/sh_customer_pricelist_view.xml',
              'views/report_xlsx_view.xml',
              'views/sh_customer_details_report.xml',
            ],
            
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "application" : True,
    "installable" : True,
    "price": 35,
    "currency": "EUR" }
