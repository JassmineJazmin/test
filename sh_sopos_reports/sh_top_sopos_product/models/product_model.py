# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields,api

class product_product(models.Model):
    _inherit = "product.product"
    
    sh_tsp_is_top_selling_product = fields.Boolean(string = "Is To Selling Product")

