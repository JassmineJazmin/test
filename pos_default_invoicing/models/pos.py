# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api

class pos_config(models.Model):
    _inherit = 'pos.config' 

    pos_defaut_invoice = fields.Boolean(string="Default Invoicing",default=True)
