# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "All In One Sales & POS Reports",
    
    "author": "Softhealer Technologies",
    
    "website": "https://www.softhealer.com",    
    
    "support": "support@softhealer.com",   

    "version": "13.0.3",
    
    "category": "Extra Tools",
    
    "license": "OPL-1",
    
    "summary": "Sales Report Based On Analysis, Compare Customer By Sales Report Module, Compare Products Based On Selling, Salesperson Wise Payment Report, Sales Report By Sales Person, Point Of Sale Report, POS Sale Report, POS Analysis Odoo",

    "description": """All in one Sales & POS (Point Of Sale) report useful to provide different POS and sales reports to do analysis. A sales &POS analysis report shows the trends that occur in a company's sales volume over time. In its most basic form, a sales & POS analysis report shows whether sales are increasing or declining.""", 
    "depends": ['base','sale','sale_management','point_of_sale','account'],
    "data": [
            "sh_payment_report_sopos/security/payment_report_security.xml",
            "sh_payment_report_sopos/security/ir.model.access.csv",
            "sh_payment_report_sopos/wizard/payment_report_wizard.xml",
            "sh_payment_report_sopos/report/payment_report.xml",
            "sh_payment_report_sopos/wizard/xls_report_view.xml",
            
            "sh_sopos_details_report/security/ir.model.access.csv",
            "sh_sopos_details_report/wizard/sale_pos_details_report_wizard.xml",
            "sh_sopos_details_report/report/sale_pos_details_report.xml",
            "sh_sopos_details_report/report/report_xlsx_view.xml",
            
            "sh_sopos_report_salesperson/security/ir.model.access.csv",
            "sh_sopos_report_salesperson/wizard/report_salesperson_wizard.xml",
            "sh_sopos_report_salesperson/views/xls_report_view.xml",
            "sh_sopos_report_salesperson/report/salesperson_report.xml",
            
            "sh_top_customers_sopos/security/ir.model.access.csv",
            "sh_top_customers_sopos/wizard/top_sopos_customer_wizard.xml",
            "sh_top_customers_sopos/report/top_sopos_customer_report.xml",
            "sh_top_customers_sopos/report/report_xlsx_view.xml",
            
            "sh_top_sopos_product/security/ir.model.access.csv",
            "sh_top_sopos_product/wizard/top_selling_wizard.xml",
            "sh_top_sopos_product/views/top_selling_view.xml",
            "sh_top_sopos_product/report/top_selling_product_report.xml",
            "sh_top_sopos_product/report/report_xlsx_view.xml",
            
    ],    
    "images": ["static/description/background.png",],             

    "installable": True,
    "auto_install": False,
    "application": True,  
    "price": 110,
    "currency": "EUR"   
}
