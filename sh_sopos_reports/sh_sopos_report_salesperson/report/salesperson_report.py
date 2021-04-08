# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
import operator


class salesperson_report(models.AbstractModel):
    _name = 'report.sh_sopos_reports.sh_sopos_sp_report_doc'
    _description = "sale person report abstract model"  

    @api.model
    def _get_report_values(self, docids, data=None):
        
        sale_order_obj = self.env["sale.order"]
        pos_order_obj = self.env["pos.order"]
        user_order_dic = {}
        user_list = []
        currency = False
        if data.get('user_ids', False):
            for user_id in data.get('user_ids'):
                order_list = []
                domain = [
                    ("date_order", ">=", data['date_start']),
                    ("date_order", "<=", data['date_end']),
                    ("user_id", "=", user_id)
                    ]
                if data.get('company_ids',False):
                    domain.append( ('company_id','in',data.get('company_ids',False)) )
                if data.get('state', False) and data.get('state') == 'done':
                    domain.append(('state', 'in', ['sale', 'done']))

                search_orders = sale_order_obj.sudo().search(domain)
                if search_orders:
                    for order in search_orders:
                        if not currency:
                            currency = order.currency_id
                            
                        order_dic = {
                            'order_number' : order.name,
                            'order_date'   : order.date_order,
                            'customer'     : order.partner_id.name if order.partner_id else "",
                            'total'        : order.amount_total,
                            'paid_amount'  : 0.0,
                            'due_amount'   : 0.0,
                            }
                        if order.invoice_ids:
                            sum_of_invoice_amount = 0.0
                            sum_of_due_amount = 0.0
                            for invoice_id in order.invoice_ids.filtered(lambda inv: inv.state not in ['cancel', 'draft']):
                                sum_of_invoice_amount += invoice_id.amount_total_signed
                                sum_of_due_amount += invoice_id.amount_residual_signed
                                
                            order_dic.update({
                                    "paid_amount" : sum_of_invoice_amount,
                                    "due_amount"  : sum_of_due_amount,
                                    })
                            
                        order_list.append(order_dic)
                
                domain = [
                    ("date_order", ">=", data['date_start']),
                    ("date_order", "<=", data['date_end']),
                    ("user_id", "=", user_id)
                    ]
                if data.get('company_ids',False):
                    domain.append( ('company_id','in',data.get('company_ids',False)) )
                if data.get('config_ids',False):
                    session_ids = self.env['pos.session'].sudo().search([('config_id','in',data.get('config_ids',False))])
                    domain.append( ('session_id','in',session_ids.ids) )
                if data.get('state', False) and data.get('state') == 'done':
                    domain.append(('state', 'in', ['paid', 'done','invoiced']))

                search_pos_orders = pos_order_obj.sudo().search(domain)
                if search_pos_orders:
                    for pos_order in search_pos_orders:
                        if not currency:
                            currency = pos_order.currency_id
                            
                        order_dic = {
                            'order_number' : pos_order.name,
                            'order_date'   : pos_order.date_order,
                            'customer'     : pos_order.partner_id.name if pos_order.partner_id else "",
                            'total'        : pos_order.amount_total,
                            'paid_amount'  : 0.0,
                            'due_amount'   : 0.0,
                            }
                        if pos_order.account_move:
                            sum_of_invoice_amount = 0.0
                            sum_of_due_amount = 0.0
                            for pos_invoice_id in pos_order.account_move.filtered(lambda inv: inv.state not in ['cancel', 'draft']):
                                sum_of_invoice_amount += pos_invoice_id.amount_total_signed
                                sum_of_due_amount += pos_invoice_id.amount_residual_signed
                                
                            order_dic.update({
                                    "paid_amount" : sum_of_invoice_amount,
                                    "due_amount"  : sum_of_due_amount,
                                    })
                            
                        order_list.append(order_dic)
                        
                search_user = self.env['res.users'].sudo().search([
                                            ('id', '=', user_id)
                                            ], limit=1)
                if search_user:
                    user_order_dic.update({search_user.name : order_list})
                    user_list.append(search_user.name)
                
        if not currency:
            currency = self.env.user.company_id.sudo().currency_id

        data = {
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'user_order_dic' :user_order_dic,
            'user_list' : user_list,
            'currency'  : currency,
        }        

        return data
