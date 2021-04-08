# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import xlwt
import base64
from io import BytesIO


class invoice_payment_report_xls(models.Model):
    _name = 'sopos.invoice.payment.report.xls'
    _description = 'Invioce Payment Xls Report'
    excel_file = fields.Binary('Download report Excel')
    file_name = fields.Char('Excel File', size=64, readonly=True)
     
    def download_report(self):
 
        return{
            'type' : 'ir.actions.act_url',
            'url':'web/content/?model=sopos.invoice.payment.report.xls&field=excel_file&download=true&id=%s&filename=%s' % (self.id, self.file_name),
            'target': 'new',
        }


class sh_payment_report_wizard(models.TransientModel):
    _name = "sh.soops.payment.report.wizard"
    _description = 'invoice payment report wizard Model'        
    
    @api.model
    def default_company_ids(self):
        is_allowed_companies = self.env.context.get('allowed_company_ids',False)
        if is_allowed_companies:
            return is_allowed_companies
        return
    
    date_start = fields.Date(string="Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date(string="End Date", required=True, default=fields.Date.today)
    
    state = fields.Selection([
            ('all', 'All'),
            ('open', 'Open'),
            ('paid', 'Paid'),
        ], string='Status', default='all') 
    
    user_ids = fields.Many2many(
            comodel_name='res.users',
            relation='rel_sh_payment_report_wizard_res_user',
            string='Salesperson')
    
    company_ids = fields.Many2many('res.company',string='Companies',default=default_company_ids)
    config_ids = fields.Many2many('pos.config',string='POS Configuration')
    
    @api.model
    def default_get(self, fields):
        rec = super(sh_payment_report_wizard, self).default_get(fields)
 
        search_users = self.env["res.users"].search([
            ('id', '=', self.env.user.id),
            ], limit=1)
        if self.env.user.has_group('sales_team.group_sale_salesman_all_leads') or self.env.user.has_group('point_of_sale.group_pos_manager'):
            rec.update({
                "user_ids" : [(6, 0, search_users.ids)],
            })
        else:
            rec.update({
                "user_ids" : [(6, 0, [self.env.user.id])],
            })
        return rec
  
    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        if self.filtered(lambda c: c.date_end and c.date_start > c.date_end):
            raise ValidationError(_('start date must be less than end date.'))    
    
    def print_report(self):
        datas = self.read()[0]

        return self.env.ref('sh_sopos_reports.sh_sopos_payment_report_action').report_action([], data=datas)        
    
    def print_xls_report(self):
        workbook = xlwt.Workbook(encoding='utf-8')
        heading_format = xlwt.easyxf('font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold = xlwt.easyxf('font:bold True,height 215;pattern: pattern solid, fore_colour gray25;align: horiz center')
        total_bold = xlwt.easyxf('font:bold True')
        bold_center = xlwt.easyxf('font:height 240,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;')
        left = xlwt.easyxf('align: horiz center;font:bold True')
        worksheet = workbook.add_sheet('Invoice Payment Report', bold_center)
        worksheet.write_merge(0, 1, 0, 7, 'Invoice Payment Report', heading_format)
        worksheet.write_merge(2, 2, 0, 7, str(self.date_start) + " to " + str(self.date_end), bold)
        account_payment_obj = self.env["account.payment"]
        account_journal_obj = self.env["account.journal"]
        pos_payment_obj = self.env["pos.payment"]
        pos_journal_obj = self.env["pos.payment.method"]
        currency = False
        j_refund = 0.0
        data = {}
        grand_journal_dic = {}
        user_data_dic = {}
        search_user = self.env['res.users'].sudo().search([('id', 'in', self.user_ids.ids)])
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
        for user_id in search_user:
            domain = [
                        ("payment_date", ">=", self.date_start),
                        ("payment_date", "<=", self.date_end),
                        ("payment_type", "in", ["inbound", "outbound"]),
                        ]
            if self.state == 'all':
                domain.append(('invoice_ids.state', 'not in', ['draft', 'cancel']))
            elif self.state == 'open':
                domain.append(('invoice_ids.state', '=', 'posted'))
            elif self.state == 'paid':
                domain.append(('invoice_ids.state', '=', 'posted')) 
            domain.append(("invoice_ids.user_id", "=", user_id.id))
            if self.company_ids:
                domain.append(('company_id','in',self.company_ids.ids))
            payments = account_payment_obj.sudo().search(domain)
            invoice_pay_dic = {}
            if payments and search_journals:
                for journal in search_journals:
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
                                        invoice_pay_dic.update({invoice.name : {journal.name : journal_wise_payment.amount, "Total" : journal_wise_payment.amount, "Invoice" : invoice.name, "Customer" : invoice.partner_id.name, "Invoice Date" : str(invoice.invoice_date), "Salesperson" : invoice.user_id.name if invoice.user_id else "", "style" :''} })
            
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
                                        invoice_pay_dic.update({invoice.name : {journal.name :-1 * (journal_wise_payment.amount), "Total" :-1 * (journal_wise_payment.amount), "Invoice" : invoice.name, "Customer" : invoice.partner_id.name, "Invoice Date" : str(invoice.invoice_date), "Salesperson" : invoice.user_id.name if invoice.user_id else "", "style" :'font:color red'} })
            
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
            
            domain = [
                        ("payment_date", ">=", self.date_start),
                        ("payment_date", "<=", self.date_end),
                        ]
            if self.state == 'all':
                domain.append(('pos_order_id.account_move.state', 'not in', ['draft', 'cancel']))
            elif self.state == 'open':
                domain.append(('pos_order_id.account_move.state', '=', 'posted'))
            elif self.state == 'paid':
                domain.append(('pos_order_id.account_move.state', '=', 'posted')) 
            domain.append(("pos_order_id.account_move.user_id", "=", user_id.id))
            if self.company_ids:
                domain.append(('company_id','in',self.company_ids.ids))
            if self.config_ids:
                session_ids = self.env['pos.session'].sudo().search([('config_id','in',self.config_ids.ids)])
                domain.append(("pos_order_id.session_id", "in", session_ids.ids))
            pos_payments = pos_payment_obj.sudo().search(domain)
            if pos_payments and search_pos_journals:
                for pos_journal in search_pos_journals:
                    for pos_journal_wise_payment in pos_payments.filtered(lambda x: x.payment_method_id.id == pos_journal.id):
                        if pos_journal_wise_payment.pos_order_id.account_move:
                            for pos_invoice in pos_journal_wise_payment.pos_order_id.account_move:
                                if not currency:
                                    currency = pos_invoice.currency_id
                                if pos_invoice.type == "out_invoice":
                                    if invoice_pay_dic.get(pos_invoice.name, False):
                                        pay_dic = invoice_pay_dic.get(pos_invoice.name)
                                        total = pay_dic.get("Total")
                                        if pay_dic.get(journal.name, False):
                                            amount = pay_dic.get(pos_journal.name)
                                            total += pos_journal_wise_payment.amount
                                            amount += pos_journal_wise_payment.amount
                                            pay_dic.update({pos_journal.name : amount, "Total" : total})
                                        else:
                                            total += pos_journal_wise_payment.amount
                                            pay_dic.update({pos_journal.name : pos_journal_wise_payment.amount, "Total" : total})
                                            
                                        invoice_pay_dic.update({pos_invoice.name : pay_dic})      
                                    else:
                                        invoice_pay_dic.update({pos_invoice.name : {pos_journal.name : pos_journal_wise_payment.amount, "Total" : pos_journal_wise_payment.amount, "Invoice" : pos_invoice.name, "Customer" : pos_invoice.partner_id.name, "Invoice Date" : str(pos_invoice.invoice_date), "Salesperson" : pos_invoice.user_id.name if pos_invoice.user_id else "", "style" :''} })
            
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
                                        invoice_pay_dic.update({pos_invoice.name : {pos_journal.name :-1 * (pos_journal_wise_payment.amount), "Total" :-1 * (pos_journal_wise_payment.amount), "Invoice" : pos_invoice.name, "Customer" : pos_invoice.partner_id.name, "Invoice Date" : str(pos_invoice.invoice_date), "Salesperson" : pos_invoice.user_id.name if pos_invoice.user_id else "", "style" :'font:color red'} })
            
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
            
            search_user = self.env['res.users'].sudo().search([
                    ('id', '=', user_id.id)
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
            'columns' : final_col_list,
            'user_data_dic' : user_data_dic,
            'grand_journal_dic' : grand_journal_dic,
        })
        row = 3
        col = 0
        
        for user in user_data_dic.keys():
            pay_list = []
            pay_list.append(user_data_dic.get(user).get('pay', []))
            row = row + 2
            worksheet.write_merge(row, row, 0, 7, "Sales Person: " + user, bold_center)
            row = row + 2
            col = 0
            for column in data.get('columns'):
                worksheet.col(col).width = int(15 * 260)
                worksheet.write(row, col, column, bold)
                col = col + 1
            for p in pay_list:
                row = row + 1
                col = 0
                for dic in p:
                    row = row + 1
                    col = 0
                    for column in data.get('columns'):
                        style = xlwt.easyxf(dic.get('style', ''))
                        worksheet.write(row, col, dic.get(column, 0), style)
                        col = col + 1
            row = row + 1
            col = 3
            worksheet.col(col).width = int(15 * 260)
            worksheet.write(row, col, "Total", total_bold)
            col = col + 1
            if user_data_dic.get(user, False):
                grand_total = user_data_dic.get(user).get('grand_total', {})
                if grand_total:
                    for column in data.get('columns'):
                        if column not in ['Invoice', 'Invoice Date', 'Salesperson', 'Customer']:
                            worksheet.write(row, col, grand_total.get(column, 0), total_bold)
                            col = col + 1
        row = row + 2
        worksheet.write_merge(row, row, 0, 1, "Payment Method", bold)
        row = row + 1
        worksheet.write(row, 0, "Name", bold)
        worksheet.write(row, 1, "Total", bold)
        for column in data.get('columns'):
            col = 0
            if column not in ["Invoice", "Invoice Date", "Salesperson", "Customer"]:
                row = row + 1
                worksheet.col(col).width = int(15 * 260)
                worksheet.write(row, col, column)
                col = col + 1
                worksheet.write(row, col, grand_journal_dic.get(column, 0))
        if grand_journal_dic.get('Refund', False):
            row = row + 1
            col = 0
            worksheet.col(col).width = int(15 * 260)
            worksheet.write(row, col, "Refund")
            worksheet.write(row, col + 1, grand_journal_dic.get('Refund', 0.0))
                    
        filename = ('Invoice Payment Report' + '.xls')
        fp = BytesIO()
        workbook.save(fp)
        
        export_id = self.env['sopos.invoice.payment.report.xls'].sudo().create({
                                                                    'excel_file': base64.encodestring(fp.getvalue()),
                                                                    'file_name': filename,
                                                                    })
        
        fp.close()
        return{
                'type': 'ir.actions.act_window',
                'res_id': export_id.id,
                'res_model': 'sopos.invoice.payment.report.xls',
                'view_mode': 'form',
                'target': 'new',
            }
