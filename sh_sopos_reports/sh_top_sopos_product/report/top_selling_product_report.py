# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, models
import operator


class TopSoposSellingReport(models.AbstractModel):
    _name = 'report.sh_sopos_reports.sh_sopos_selling_pr_doc'
    _description = "top selling product report abstract model"    

    @api.model
    def _get_report_values(self, docids, data=None):

        data = dict(data or {})

        sale_order_line_obj = self.env['sale.order.line']
        pos_order_line_obj = self.env['pos.order.line']
        ##################################
        # for product from to
        domain = [
            ('order_id.state', 'in', ['sale', 'done']),
        ]
        if data.get('company_ids', False):
            domain.append(('order_id.company_id', 'in',
                           data.get('company_ids', False)))
        if data.get('date_from', False):
            domain.append(('order_id.date_order', '>=', data.get('date_from')))
        if data.get('date_to', False):
            domain.append(('order_id.date_order', '>=', data.get('date_to')))

        if data.get('team_id'):
            team_id = data.get('team_id')
            team_id = team_id[0]
            domain.append(
                ('order_id.team_id', '=', team_id)
            )

        # search order line product and add into product_qty_dictionary
        search_order_lines = sale_order_line_obj.sudo().search(domain)

        product_total_qty_dic = {}
        if search_order_lines:
            for line in search_order_lines.sorted(key=lambda o: o.product_id.id):

                if product_total_qty_dic.get(line.product_id.name, False):
                    qty = product_total_qty_dic.get(line.product_id.name)
                    qty += line.product_uom_qty
                    product_total_qty_dic.update({line.product_id.name: qty})
                else:
                    product_total_qty_dic.update(
                        {line.product_id.name: line.product_uom_qty})

        final_product_list = []
        final_product_qty_list = []
        if product_total_qty_dic:
            # sort partner dictionary by descending order
            sorted_product_total_qty_list = sorted(
                product_total_qty_dic.items(), key=operator.itemgetter(1), reverse=True)
            counter = 0

            for tuple_item in sorted_product_total_qty_list:
                if data['product_uom_qty'] != 0 and tuple_item[1] >= data['product_uom_qty']:
                    final_product_list.append(tuple_item[0])

                elif data['product_uom_qty'] == 0:
                    final_product_list.append(tuple_item[0])

                final_product_qty_list.append(tuple_item[1])
                # only show record by user limit
                counter += 1
                if counter >= data['no_of_top_item']:
                    break
        ##################################
        # for Compare product from to
        search_order_lines = False
        domain = [
            ('order_id.state', 'in', ['sale', 'done']),
        ]
        if data.get('company_ids', False):
            domain.append(('order_id.company_id', 'in',
                           data.get('company_ids', False)))
        if data.get('date_compare_from', False):
            domain.append(('order_id.date_order', '>=',
                           data.get('date_compare_from')))
        if data.get('date_compare_to', False):
            domain.append(('order_id.date_order', '>=',
                           data.get('date_compare_to')))

        if data.get('team_id'):
            team_id = data.get('team_id')
            team_id = team_id[0]
            domain.append(
                ('order_id.team_id', '=', team_id)
            )

        search_order_lines = sale_order_line_obj.sudo().search(domain)

        product_total_qty_dic = {}
        if search_order_lines:
            for line in search_order_lines.sorted(key=lambda o: o.product_id.id):

                if product_total_qty_dic.get(line.product_id.name, False):
                    qty = product_total_qty_dic.get(line.product_id.name)
                    qty += line.product_uom_qty
                    product_total_qty_dic.update({line.product_id.name: qty})
                else:
                    product_total_qty_dic.update(
                        {line.product_id.name: line.product_uom_qty})

        final_compare_product_list = []
        final_compare_product_qty_list = []
        if product_total_qty_dic:
            # sort partner dictionary by descending order
            sorted_product_total_qty_list = sorted(
                product_total_qty_dic.items(), key=operator.itemgetter(1), reverse=True)
            counter = 0

            for tuple_item in sorted_product_total_qty_list:
                if data['product_uom_qty'] != 0 and tuple_item[1] >= data['product_uom_qty']:
                    final_compare_product_list.append(tuple_item[0])

                elif data['product_uom_qty'] == 0:
                    final_compare_product_list.append(tuple_item[0])

                final_compare_product_qty_list.append(tuple_item[1])
                # only show record by user limit
                counter += 1
                if counter >= data['no_of_top_item']:
                    break
        final_product_list = []
        final_product_qty_list = []
        domain = [
            ('order_id.state', 'in', ['paid', 'done', 'invoiced']),
        ]
        if data.get('company_ids', False):
            domain.append(('order_id.company_id', 'in',
                           data.get('company_ids', False)))
        if data.get('config_ids', False):
            session_ids = self.env['pos.session'].sudo().search(
                [('config_id', 'in', data.get('config_ids', False))])
            domain.append(('order_id.session_id', 'in', session_ids.ids))
        if data.get('date_from', False):
            domain.append(('order_id.date_order', '>=', data.get('date_from')))
        if data.get('date_to', False):
            domain.append(('order_id.date_order', '>=', data.get('date_to')))

        # search order line product and add into product_qty_dictionary
        search_pos_order_lines = pos_order_line_obj.sudo().search(domain)

        if search_pos_order_lines:
            for pos_line in search_pos_order_lines.sorted(key=lambda o: o.product_id.id):

                if product_total_qty_dic.get(pos_line.product_id.name, False):
                    qty = product_total_qty_dic.get(pos_line.product_id.name)
                    qty += pos_line.qty
                    product_total_qty_dic.update(
                        {pos_line.product_id.name: qty})
                else:
                    product_total_qty_dic.update(
                        {pos_line.product_id.name: pos_line.qty})

        if product_total_qty_dic:
            # sort partner dictionary by descending order
            sorted_product_total_qty_list = sorted(
                product_total_qty_dic.items(), key=operator.itemgetter(1), reverse=True)
            counter = 0

            for tuple_item in sorted_product_total_qty_list:
                if data['product_uom_qty'] != 0 and tuple_item[1] >= data['product_uom_qty']:
                    final_product_list.append(tuple_item[0])

                elif data['product_uom_qty'] == 0:
                    final_product_list.append(tuple_item[0])

                final_product_qty_list.append(tuple_item[1])
                # only show record by user limit
                counter += 1
                if counter >= data['no_of_top_item']:
                    break

        ##################################
        # for Compare product from to
        search_pos_order_lines = False
        domain = [
            ('order_id.state', 'in', ['paid', 'done', 'invoiced']),
        ]
        if data.get('company_ids', False):
            domain.append(('order_id.company_id', 'in',
                           data.get('company_ids', False)))
        if data.get('config_ids', False):
            session_ids = self.env['pos.session'].sudo().search(
                [('config_id', 'in', data.get('config_ids', False))])
            domain.append(('order_id.session_id', 'in', session_ids.ids))
        if data.get('date_compare_from', False):
            domain.append(('order_id.date_order', '>=',
                           data.get('date_compare_from')))
        if data.get('date_compare_to', False):
            domain.append(('order_id.date_order', '>=',
                           data.get('date_compare_to')))

        search_pos_order_lines = pos_order_line_obj.sudo().search(domain)
        product_total_qty_dic = {}
        if search_pos_order_lines:
            for pos_line in search_pos_order_lines.sorted(key=lambda o: o.product_id.id):

                if product_total_qty_dic.get(pos_line.product_id.name, False):
                    qty = product_total_qty_dic.get(pos_line.product_id.name)
                    qty += pos_line.qty
                    product_total_qty_dic.update(
                        {pos_line.product_id.name: qty})
                else:
                    product_total_qty_dic.update(
                        {pos_line.product_id.name: pos_line.qty})

        if product_total_qty_dic:
            # sort partner dictionary by descending order
            sorted_product_total_qty_list = sorted(
                product_total_qty_dic.items(), key=operator.itemgetter(1), reverse=True)
            counter = 0

            for tuple_item in sorted_product_total_qty_list:
                if data['product_uom_qty'] != 0 and tuple_item[1] >= data['product_uom_qty']:
                    final_compare_product_list.append(tuple_item[0])

                elif data['product_uom_qty'] == 0:
                    final_compare_product_list.append(tuple_item[0])

                final_compare_product_qty_list.append(tuple_item[1])
                # only show record by user limit
                counter += 1
                if counter >= data['no_of_top_item']:
                    break

        # find lost and new partner here
        lost_product_list = []
        new_product_list = []
        if final_product_list and final_compare_product_list:
            for item in final_product_list:
                if item not in final_compare_product_list:
                    lost_product_list.append(item)

            for item in final_compare_product_list:
                if item not in final_product_list:
                    new_product_list.append(item)

        data.update({'products': final_product_list,
                     'products_qty': final_product_qty_list,
                     'compare_products': final_compare_product_list,
                     'compare_products_qty': final_compare_product_qty_list,
                     'lost_products': lost_product_list,
                     'new_products': new_product_list,
                     })

        return data

