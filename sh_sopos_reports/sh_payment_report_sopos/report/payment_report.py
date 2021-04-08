# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
import operator


class payment_report(models.AbstractModel):
    _name = 'report.sh_sopos_reports.sh_sopos_report_doc'
    _description = 'invoice payment report abstract model'    

    @api.model
    def _get_report_values(self, docids, data=None):
        
        data = dict(data or {})
        account_payment_obj = self.env["account.payment"]
        account_journal_obj = self.env["account.journal"]
        
        pos_payment_obj = self.env["pos.payment"]
        pos_journal_obj = self.env["pos.payment.method"]
        
        search_journals = account_journal_obj.sudo().search([
            ('type', 'in', ['bank', 'cash'])
            ])
        
        search_pos_journals = pos_journal_obj.sudo().search([])
        
        
        final_col_list = ["Invoice", "Invoice Date", "Salesperson", "Customer"]
        final_total_col_list = []
        
        for journal in search_journals:
            if journal.name not in final_col_list:
                final_col_list.append(journal.name)
            if journal.name not in final_total_col_list:
                final_total_col_list.append(journal.name)
        
        for pos_journal in search_pos_journals:
            if pos_journal.name not in final_col_list:
                final_col_list.append(pos_journal.name)
            if pos_journal.name not in final_total_col_list:
                final_total_col_list.append(pos_journal.name)
        
        final_col_list.append("Total")
        final_total_col_list.append("Total")
                
        currency = False
        grand_journal_dic = {}
        j_refund = 0.0        
        
        user_data_dic = {}
        if data.get("user_ids", False):

            for user_id in data.get("user_ids"):
                
                domain = [
                    ("payment_date", ">=", data["date_start"]),
                    ("payment_date", "<=", data["date_end"]),
                    ("payment_type", "in", ["inbound", "outbound"]),
                    ]
                if data.get("state", False):
                    state = data.get("state")
                    if state == 'all':
                        domain.append(('invoice_ids.state', 'not in', ['draft', 'cancel']))
                    elif state == 'open':
                        domain.append(('invoice_ids.state', '=', 'posted'))
                    elif state == 'paid':
                        domain.append(('invoice_ids.state', '=', 'posted'))                
                
                domain.append(("invoice_ids.invoice_user_id", "=", user_id))  
                if data.get('company_ids',False):
                    domain.append(("company_id", "in", data.get('company_ids',False)))                
                payments = account_payment_obj.sudo().search(domain)
                invoice_pay_dic = {}
                if payments and search_journals:
                    for journal in search_journals:
        
                        # journal wise payment first we total all bank, cash etc etc.
                        
                        for journal_wise_payment in payments.filtered(lambda x: x.journal_id.id == journal.id):
                            if journal_wise_payment.invoice_ids:
                                for invoice in journal_wise_payment.invoice_ids:
                                    
                                    if not currency:
                                        currency = invoice.currency_id
                                        
                                    if invoice.type == "out_invoice":
                                        if invoice_pay_dic.get(invoice.name, False):
                                            pay_dic = invoice_pay_dic.get(invoice.name)
                                            total = pay_dic.get("Total")
                                            if pay_dic.get(journal.name, False):
                                                amount = pay_dic.get(journal.name)
                                                total += journal_wise_payment.amount
                                                amount += journal_wise_payment.amount
                                                pay_dic.update({journal.name : amount, "Total" : total})
                                            else:
                                                total += journal_wise_payment.amount
                                                pay_dic.update({journal.name : journal_wise_payment.amount, "Total" : total})
                                                
                                            invoice_pay_dic.update({invoice.name : pay_dic})      
                                        else:
                                            invoice_pay_dic.update({invoice.name : {journal.name : journal_wise_payment.amount, "Total" : journal_wise_payment.amount, "Invoice" : invoice.name, "Customer" : invoice.partner_id.name, "Invoice Date" : invoice.invoice_date, "Salesperson" : invoice.invoice_user_id.name if invoice.invoice_user_id else "", "style" :'border: 1px solid black;'} })
                
                                    if invoice.type == "out_refund":
                                        j_refund += journal_wise_payment.amount
                                        if invoice_pay_dic.get(invoice.name, False):
                                            pay_dic = invoice_pay_dic.get(invoice.name)
                                            total = pay_dic.get("Total")
                                            if pay_dic.get(journal.name, False):
                                                amount = pay_dic.get(journal.name)
                                                total -= journal_wise_payment.amount
                                                amount -= journal_wise_payment.amount
                                                pay_dic.update({journal.name : amount, "Total" : total})
                                            else:
                                                total -= journal_wise_payment.amount
                                                pay_dic.update({journal.name :-1 * (journal_wise_payment.amount), "Total" : total})
                                                
                                            invoice_pay_dic.update({invoice.name : pay_dic})
             
                                        else:
                                            invoice_pay_dic.update({invoice.name : {journal.name :-1 * (journal_wise_payment.amount), "Total" :-1 * (journal_wise_payment.amount), "Invoice" : invoice.name, "Customer" : invoice.partner_id.name, "Invoice Date" : invoice.invoice_date, "Salesperson" : invoice.invoice_user_id.name if invoice.invoice_user_id else "", "style" :'border: 1px solid black;color:red'} })
                            
                # all final list and [{},{},{}] format
                # here we get the below total.
                # total journal amount is a grand total and format is : {} just a dictionary
                final_list = []
                total_journal_amount = {}
                for key, value in invoice_pay_dic.items():
                    final_list.append(value)
                    for col_name in final_total_col_list:
                        if total_journal_amount.get(col_name, False):
                            total = total_journal_amount.get(col_name)
                            total += value.get(col_name, 0.0)
                            
                            total_journal_amount.update({col_name: total})
                            
                        else:
                            total_journal_amount.update({col_name : value.get(col_name, 0.0)})
                
                # finally make user wise dic here.
                search_user = self.env['res.users'].sudo().search([
                    ('id', '=', user_id)
                    ], limit=1)
                if search_user:
                    user_data_dic.update({
                        search_user.name : {'pay' : final_list, 'grand_total' : total_journal_amount}
                    })
                    
#                 for col_name in final_total_col_list:
#                     j_total = 0.0
#                     j_total = total_journal_amount.get(col_name, 0.0)
#                     j_total += grand_journal_dic.get(col_name, 0.0)
#                     grand_journal_dic.update({col_name : j_total})
                
                
                domain = [
                    ("payment_date", ">=", data["date_start"]),
                    ("payment_date", "<=", data["date_end"]),
                    ]
#                     
                if data.get("state", False):
                    state = data.get("state")
                    if state == 'all':
                        domain.append(('pos_order_id.account_move.state', 'not in', ['draft', 'cancel']))
                    elif state == 'open':
                        domain.append(('pos_order_id.account_move.state', '=', 'posted'))
                    elif state == 'paid':
                        domain.append(('pos_order_id.account_move.state', '=', 'posted'))                
                 
                domain.append(("pos_order_id.account_move.invoice_user_id", "=", user_id))  
                if data.get('company_ids',False):
                    domain.append(("company_id", "in", data.get('company_ids',False)))     
                if data.get('config_ids',False):
                    session_ids = self.env['pos.session'].sudo().search([('config_id','in',data.get('config_ids',False))])
                    domain.append(("pos_order_id.session_id", "in", session_ids.ids))           
                pos_payments = pos_payment_obj.sudo().search(domain)
                invoice_pay_dic = {}
                if pos_payments and search_pos_journals:
                    for pos_journal in search_pos_journals:
         
                        # journal wise payment first we total all bank, cash etc etc.
                         
                        for pos_journal_wise_payment in pos_payments.filtered(lambda x: x.payment_method_id.id == pos_journal.id):
                            if pos_journal_wise_payment.pos_order_id.account_move:
                                for pos_invoice in pos_journal_wise_payment.pos_order_id.account_move:
                                    if not currency:
                                        currency = pos_invoice.currency_id
                                         
                                    if pos_invoice.type == "out_invoice":
                                        if invoice_pay_dic.get(pos_invoice.name, False):
                                            pay_dic = invoice_pay_dic.get(pos_invoice.name)
                                            total = pay_dic.get("Total")
                                            if pay_dic.get(pos_journal.name, False):
                                                amount = pay_dic.get(pos_journal.name)
                                                total += pos_journal_wise_payment.amount
                                                amount += pos_journal_wise_payment.amount
                                                pay_dic.update({pos_journal.name : amount, "Total" : total})
                                            else:
                                                total += pos_journal_wise_payment.amount
                                                pay_dic.update({pos_journal.name : pos_journal_wise_payment.amount, "Total" : total})
                                                 
                                            invoice_pay_dic.update({pos_invoice.name : pay_dic})      
                                        else:
                                            invoice_pay_dic.update({pos_invoice.name : {pos_journal.name : pos_journal_wise_payment.amount, "Total" : pos_journal_wise_payment.amount, "Invoice" : pos_invoice.name, "Customer" : pos_invoice.partner_id.name, "Invoice Date" : pos_invoice.invoice_date, "Salesperson" : pos_invoice.invoice_user_id.name if pos_invoice.invoice_user_id else "", "style" :'border: 1px solid black;'} })
                 
                                    if pos_invoice.type == "out_refund":
                                        j_refund += pos_journal_wise_payment.amount
                                        if invoice_pay_dic.get(pos_invoice.name, False):
                                            pay_dic = invoice_pay_dic.get(pos_invoice.name)
                                            total = pay_dic.get("Total")
                                            if pay_dic.get(pos_journal.name, False):
                                                amount = pay_dic.get(pos_journal.name)
                                                total -= pos_journal_wise_payment.amount
                                                amount -= pos_journal_wise_payment.amount
                                                pay_dic.update({pos_journal.name : amount, "Total" : total})
                                            else:
                                                total -= pos_journal_wise_payment.amount
                                                pay_dic.update({pos_journal.name :-1 * (pos_journal_wise_payment.amount), "Total" : total})
                                                 
                                            invoice_pay_dic.update({pos_invoice.name : pay_dic})
              
                                        else:
                                            invoice_pay_dic.update({pos_invoice.name : {pos_journal.name :-1 * (pos_journal_wise_payment.amount), "Total" :-1 * (pos_journal_wise_payment.amount), "Invoice" : pos_invoice.name, "Customer" : pos_invoice.partner_id.name, "Invoice Date" : pos_invoice.invoice_date, "Salesperson" : pos_invoice.invoice_user_id.name if pos_invoice.invoice_user_id else "", "style" :'border: 1px solid black;color:red'} })
                             
#                 # all final list and [{},{},{}] format
#                 # here we get the below total.
#                 # total journal amount is a grand total and format is : {} just a dictionary
                for key, value in invoice_pay_dic.items():
                    final_list.append(value)
                    for col_name in final_total_col_list:
                        if total_journal_amount.get(col_name, False):
                            total = total_journal_amount.get(col_name)
                            total += value.get(col_name, 0.0)
                             
                            total_journal_amount.update({col_name: total})
                             
                        else:
                            total_journal_amount.update({col_name : value.get(col_name, 0.0)})
                 
                # finally make user wise dic here.
                search_user = self.env['res.users'].sudo().search([
                    ('id', '=', user_id)
                    ], limit=1)
                if search_user:
                    user_data_dic.update({
                        search_user.name : {'pay' : final_list, 'grand_total' : total_journal_amount}
                    })
                     
                for col_name in final_total_col_list:
                    j_total = 0.0
                    j_total = total_journal_amount.get(col_name, 0.0)
                    j_total += grand_journal_dic.get(col_name, 0.0)
                    grand_journal_dic.update({col_name : j_total})
            
            j_refund = j_refund * -1
            grand_journal_dic.update({'Refund' : j_refund})
                
        data.update({
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'columns' : final_col_list,
            'user_data_dic' : user_data_dic,
            'currency' : currency,
            'grand_journal_dic' : grand_journal_dic,
        })        
        
        return data
