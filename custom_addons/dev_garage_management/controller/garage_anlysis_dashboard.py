import datetime
from odoo import http
from odoo.http import request
from odoo import models, fields, api, _
from operator import itemgetter
import itertools
import operator
from datetime import date, timedelta
from collections import defaultdict
import calendar
from itertools import chain
from datetime import datetime, timedelta, date

class ProjectFilter(http.Controller):
    """The ProjectFilter class provides the filter option to the js.
    When applying the filter returns the corresponding data."""



    @http.route('/garage/all_filter', auth='public', type='json')
    def all_filter(self):
        user_list =[]
        customer_list = []

        user_ids = request.env['res.users'].search([])
        customer_ids = request.env['res.partner'].search([])
       

        for user_id in user_ids:
            dic = {'name': user_id.name,
                   'id': user_id.id}
            user_list.append(dic)

        for customer_id in customer_ids:
            dict = {'name': customer_id.name, 'id': customer_id.id}
            customer_list.append(dict)
        
        return [user_list,customer_list]

    @http.route('/get/garage/tiles/data', auth='public', type='json')
    def get_tiles_data(self, **kwargs):
        today = date.today()
        lead_domain =[('service_id','!=',False)]
        rfq_domain =[]
        sales_domain =[]
        project_task_domain = []
        invoice_domain =[]
        request_domain = []
        if not kwargs.get('duration'):
            lead_domain += [('create_date', '>=', today),('create_date', '<=', today)]
            rfq_domain +=  [('date_order', '>=', today),('date_order', '<=', today)]
            sales_domain += [('sale_id.date_order', '>=', today), ('sale_id.date_order', '<=', today)]
            # invoice_domain += [('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]
            request_domain += [('request_date', '>=', today), ('request_date', '<=', today)]
            project_task_domain += [('create_date', '>=', today), ('create_date', '<=', today)]

        if kwargs:
            if kwargs['partner_id']:
                if kwargs['partner_id'] != 'all':
                    partner_id = int(kwargs['partner_id'])
                    lead_domain += [('partner_id', '=', partner_id)]
                    rfq_domain += [('partner_id','=',partner_id)]
                    sales_domain += [('partner_id','=',partner_id)]
                    invoice_domain += [('partner_id','=',partner_id)]
                    request_domain += [('customer_id','=',partner_id)]
                    project_task_domain+= [('partner_id','=',partner_id)]

            if kwargs['user_id']:
                if kwargs['user_id'] != 'all':
                    user_id = int(kwargs['user_id'])
                    lead_domain += [('user_id', '=', user_id)]
                    rfq_domain += [('user_id','=',user_id)]
                    sales_domain += [('user_id','=',user_id)]
                    invoice_domain += [('user_id','=',user_id)]
                    request_domain += [('user_id','=',user_id)]
                    project_task_domain+= [('user_ids','in',[user_id])]

            if kwargs['duration']:
                duration = kwargs['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    lead_domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]
                    rfq_domain +=[('date_order', '>=', filter_date), ('date_order', '<=', today)]
                    sales_domain += [('sale_id.date_order', '>=', filter_date), ('sale_id.date_order', '<=', today)]
                    invoice_domain += [('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]
                    request_domain += [('request_date', '>=', filter_date), ('request_date', '<=', today)]
                    project_task_domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]
  
        due_invoice_list =[]
        paid_invoice_list=[]
        draft_job_card = []
        confirm_job_card = []
        in_process_job_card =[]
        total_diagnosis =[]
        total_sales_ids =[]
        print("lead_domain===================",lead_domain)
        total_lead = request.env['crm.lead'].search([('type','=','lead')]+lead_domain)
        print("lead_domaintotal_lead==============",total_lead)
        total_won_lead = request.env['crm.lead'].search([('type','=','opportunity')]+lead_domain)
        total_rfq = request.env['purchase.order'].search([('project_task_id','!=',False),('state','=','draft')]+rfq_domain)
        total_sales_id_list = request.env['project.task'].search(sales_domain)

        for sales in total_sales_id_list:
            if sales.sale_id:
                total_sales_ids.append(sales.sale_id.id)
        

        total_work_order=request.env['project.task'].search([('task_type','=','work_order')]+project_task_domain)

        total_sales_id_list = request.env['project.task'].search(project_task_domain)
        valid_sale_order_ids = [task.sale_id.id for task in total_sales_id_list if task.sale_id]

        invoice_ids = []
        if valid_sale_order_ids:
            sale_orders = request.env['sale.order'].search([('id', 'in', valid_sale_order_ids)])
            for order in sale_orders:
                for inv in order.invoice_ids:
                    invoice_ids.append(inv.id)

        due_invoice_list = []
        paid_invoice_list = []
        if invoice_ids:
            final_invoice_domain = [('id', 'in', invoice_ids)] + invoice_domain
            all_invoice_ids = request.env['account.move'].search(final_invoice_domain)
            for invoice_id in all_invoice_ids:
                if invoice_id.state == 'draft':
                    due_invoice_list.append(invoice_id.id)
                if invoice_id.state == 'posted' and invoice_id.payment_state == 'paid':
                    paid_invoice_list.append(invoice_id.id)

        total_request = request.env['dev.repair.request'].search(request_domain)
        for job_card in total_request:
            if job_card.state =="draft":
                draft_job_card.append(job_card.id)
            if job_card.state =="confirm":
                confirm_job_card.append(job_card.id)
            if job_card.state =="in_progress":
                in_process_job_card.append(job_card.id)
        
        total_diagnosis =request.env['project.task'].search([('task_type','=','diagnosys')]+project_task_domain)
        
        user_name = request.env.user.name
        user_img = request.env.user.image_1920  
        company_currency = request.env.user.company_id.currency_id.name

        return {
            'total_won_lead':total_won_lead.ids,
            'total_lead':total_lead.ids,
            'total_work_order':total_work_order.ids,
            'draft_job_card':draft_job_card,
            'confirm_job_card':confirm_job_card,
            'in_process_job_card':in_process_job_card,
            'total_diagnosis':total_diagnosis.ids,
            'due_invoice_list':due_invoice_list,
            'paid_invoice_list':paid_invoice_list,
            'total_request':total_request.ids,
            'total_rfq':total_rfq.ids,
            'total_sales_ids':total_sales_ids,
            'user_img': user_img,
            'user_name': user_name,
            'company_currency':company_currency,

        }
    

# Job card by Team

    @http.route('/garage/job_card/chart/data', auth='public', type='json')
    def get_job_card_chart_data(self, **kw):
        all_color_list = [
            '#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
            '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad'
        ]

        data = kw.get('data')
        today = date.today()
        request_domain =[]

        if not data.get('duration'):
            request_domain += [('request_date', '>=', today),('request_date', '<=', today)]
           
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    request_domain += [('user_id', '=', user_id)]
            if data['customer_id']:
                if data['customer_id'] != 'all':
                    partner_id = int(data['customer_id'])
                    request_domain += [('customer_id', '=', partner_id)]
                    
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    request_domain += [('request_date', '>=', filter_date), ('request_date', '<=', today)]

        all_team_ids = request.env['crm.team'].search([])
        team_labels = [team.name for team in all_team_ids]
        all_job_cards = request.env['dev.repair.request'].search(request_domain)

        team_lead_ids_lst = []  
        team_detail_ids_lst = [] 

        for team in all_team_ids:
            job_card_ids = all_job_cards.filtered(lambda jc: jc.team_id.id == team.id).mapped('id')
            team_lead_ids_lst.append([len(job_card_ids)])  
            team_detail_ids_lst.append(job_card_ids)      

        team_wise_job_card_chart_data = {
            'labels': team_labels,
            'datasets': [{
                'label': "Job Card By Team",
                'backgroundColor': all_color_list[:len(team_labels)],
                'data': team_lead_ids_lst,
                'detail': team_detail_ids_lst  
            }]
        }

        return {
            'team_wise_job_card_chart_data': team_wise_job_card_chart_data
        }



# Job card by State

    @http.route('/garage/job_card/state/chart/data', auth='public', type='json')
    def get_job_card_by_state_chart_data(self, **kw):
        all_color_list = [
            '#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
            '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad'
        ]

        data = kw.get('data')
        today = date.today()
        request_domain =[]
        if not data.get('duration'):
            request_domain += [('request_date', '>=', today),('request_date', '<=', today)]
           
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    request_domain += [('user_id', '=', user_id)]
            if data['customer_id']:
                if data['customer_id'] != 'all':
                    partner_id = int(data['customer_id'])
                    request_domain += [('customer_id', '=', partner_id)]
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    request_domain += [('request_date', '>=', filter_date), ('request_date', '<=', today)]

        state_labels = ["draft", "assign", "confirm", "in_progress", "done"]
        Labels = ["Draft", "Assign", "Confirm", "In Progress", "Done"]
        all_job_cards = request.env['dev.repair.request'].search(request_domain)
        state_counts_list = []    
        state_details_list = []   
        for state in state_labels:
            job_cards_in_state = all_job_cards.filtered(lambda jc: jc.state == state)
            job_card_ids = job_cards_in_state.mapped('id')
            state_counts_list.append([len(job_card_ids)])  
            state_details_list.append(job_card_ids)        
        state_wise_job_card_chart_data = {
            'labels': Labels,
            'datasets': [{
                'label': "Job Cards By State",
                'backgroundColor': all_color_list[:len(state_labels)],
                'data': state_counts_list,
                'detail': state_details_list
            }]
        }
        return {
            'state_wise_job_card_chart_data': state_wise_job_card_chart_data
        }
        
 
#  Top due invoice by chart


    @http.route('/customer/due/invoice/chart/data', auth='public', type='json')
    def get_customer_due_invoice_chart_data(self, **kw):
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']

        today = date.today()
        data = kw.get('data', {})
        invoice_domain =[]
        top_due_invoice_select = data.get('top_due_invoice_select')
        if not data.get('duration'):
            invoice_domain += [('invoice_ids.invoice_date', '>=', today),('invoice_ids.invoice_date', '<=', today)]
           
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    invoice_domain += [('user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    invoice_domain += [('partner_id', '=', partner_id)]

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    invoice_domain += [('invoice_ids.invoice_date', '>=', filter_date), ('invoice_ids.invoice_date', '<=', today)]

        total_sales_id_list = request.env['project.task'].search([])
        valid_sale_order_ids = [task.sale_id.id for task in total_sales_id_list if task.sale_id]

        if valid_sale_order_ids:
            sale_order_domain = [('id', 'in', valid_sale_order_ids)]
            sale_orders = request.env['sale.order'].search(sale_order_domain+invoice_domain)
        else:
            sale_orders = request.env['sale.order'].browse([])

        due_invoice_records = []
        for order in sale_orders:
            for inv in order.invoice_ids.filtered(lambda i: i.state == 'posted' and i.payment_state == 'not_paid'):
                due_invoice_records.append(inv)

        inv_data_by_customer = {}
        for invoice in due_invoice_records:
            if invoice.partner_id:
                partner_name = invoice.partner_id.name
                if partner_name not in inv_data_by_customer:
                    inv_data_by_customer[partner_name] = {
                        'amount_due': 0,
                        'invoice_ids': []
                    }
                inv_data_by_customer[partner_name]['amount_due'] += invoice.amount_residual
                inv_data_by_customer[partner_name]['invoice_ids'].append(invoice.id)

        sorted_due_customers = sorted(inv_data_by_customer.items(), key=lambda x: x[1]['amount_due'], reverse=True)[0:int(top_due_invoice_select)]
        final_due_chart_record = sorted_due_customers

        top_invoice_customer_chart = []
        top_invoice_customer_repeat_time = []
        due_invoice_ids_lst = []

        for partner_name, data in final_due_chart_record:
            top_invoice_customer_chart.append(partner_name)
            top_invoice_customer_repeat_time.append(data['amount_due'])
            due_invoice_ids_lst.append(data['invoice_ids'])

        due_invoice_chart_data = {
            'labels': top_invoice_customer_chart,
            'datasets': [{
                'label': "Customer",
                'backgroundColor': all_color_list[:len(top_invoice_customer_chart)],
                'data': top_invoice_customer_repeat_time,
                'detail': due_invoice_ids_lst
            }]
        }
        return {
            'due_invoice_chart_data': due_invoice_chart_data,
        }


    # Top Product Selling
    @http.route('/top/product/selling/chart/data', auth='public', type='json')
    def get_top_product_selling_chart_data(self, **kw):
        
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']     
    
        data=kw['data']
        order_domain = []
        top_product_selling_count=data['top_product_selling_count']
        
        today = date.today()
        
        if not data.get('duration'):
            order_domain = [('create_date', '>=', today ),('create_date', '<=', today )]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    order_domain += [('order_id.user_id','=',user_id)]
                    
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    order_domain += [('order_partner_id','=',partner_id)]
                    

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    order_domain += [('order_id.date_order', '>=', filter_date), ('order_id.date_order', '<=', today)]

        top_selling_product=[]
        top_selling_product_chart=[]
        top_selling_product_repeat_time=[]
        total_sales_id_list = request.env['project.task'].search([])
        valid_sale_order_ids = []

        for sales in total_sales_id_list:
            if sales.sale_id:
                valid_sale_order_ids.append(sales.sale_id.id)

        if valid_sale_order_ids:
            sale_line_domain = [('order_id', 'in', valid_sale_order_ids)]
            top_selling_order = request.env['sale.order.line'].search(sale_line_domain+order_domain)
        else:
            top_selling_order = request.env['sale.order.line'].browse([])  # Empty recordset

        
        sale_data = []
        for s_data in top_selling_order:

            sale_data.append({
                                'product_template_id':s_data.product_template_id.name or 'None',
                                'id':s_data.id or False,
                                'price_subtotal':s_data.price_subtotal or 'None',
            })
        
        n_lines = sorted(sale_data, key=itemgetter('product_template_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('product_template_id'))
        lines = [{'product_template_id': k, 'values': [x for x in v]} for k, v in groups]

        product_ids_lst=[]
        for x in lines:
            product_id_lst = []
            for id in x['values']:
                product_id_lst.append(id['id'])
            product_ids_lst.append(product_id_lst)
            product_ids_lst=sorted(product_ids_lst, key=lambda x: len(x), reverse=True)

        for line in lines:
            top_selling_product.append(
                {'product': line.get('product_template_id')[0:], 'repeated_time': len(line.get('values'))})
        top_selling_product = (sorted(top_selling_product, key=lambda i: i['repeated_time'], reverse=True))[0:int(top_product_selling_count)]
        for rep_product_data in top_selling_product:
            top_selling_product_chart.append(rep_product_data.get('product'))
            top_selling_product_repeat_time.append(rep_product_data.get('repeated_time'))

        top_selling_product_chart_data = {
            'labels': top_selling_product_chart,
            'datasets': [{
                'label': "Top Selling Products",
                'backgroundColor': all_color_list[:len(top_selling_product_chart)],
                'data': top_selling_product_repeat_time,
                'detail':product_ids_lst
            }]
        }
        return{
            'top_selling_product_chart_data': top_selling_product_chart_data
        }


# Top customer by revenue
    @http.route('/top/customer/revenue/chart/data', auth='public', type='json')
    def get_top_customer_revenue_chart_data(self, **kw):
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']

        data = kw.get('data')
        today = date.today()
        sale_domain = []
        sale_order_domain = []
        top_cust_revenue_count=data['top_cust_revenue_count']
        
        today = date.today()
        
        if not data.get('duration'):
            sale_domain = [('date_order', '>=', today ),('date_order', '<=', today )]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    sale_domain += [('user_id','=',user_id)]
                    
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    sale_domain += [('partner_id','=',partner_id)]
                    
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    sale_domain += [('date_order', '>=', filter_date), ('date_order', '<=', today)]


        total_sales_id_list = request.env['project.task'].search([])
        valid_sale_order_ids = [sales.sale_id.id for sales in total_sales_id_list if sales.sale_id]

        if valid_sale_order_ids:
            sale_order_domain = [('id', 'in', valid_sale_order_ids)]
            sale_orders = request.env['sale.order'].search(sale_order_domain + sale_domain)
        else:
            sale_orders = request.env['sale.order'].browse([])

        revenue_by_customer = {}
        detail_by_customer = {}

        for order in sale_orders:
            customer_name = order.partner_id.name or order.partner_id

            if customer_name in revenue_by_customer:
                revenue_by_customer[customer_name] += order.amount_total
                detail_by_customer[customer_name].append(order.id)
            else:
                revenue_by_customer[customer_name] = order.amount_total
                detail_by_customer[customer_name] = [order.id]

        # Step 3: Sort by revenue and prepare chart data
        sorted_customers = sorted(revenue_by_customer.items(), key=lambda x: x[1], reverse=True)[0:int(top_cust_revenue_count)]

        customer_names = []
        customer_revenue = []
        customer_details = []

        for name, total in sorted_customers:
            customer_names.append(name)
            customer_revenue.append(total)
            customer_details.append(detail_by_customer[name])

        top_cust_revenue_chart_data = {
            'labels': customer_names,
            'datasets': [{
                'label': "Top Customers by Revenue",
                'backgroundColor': all_color_list[:len(customer_names)],
                'data': customer_revenue,
                'detail': customer_details
            }]
        }
        return {
            'top_cust_revenue_chart_data': top_cust_revenue_chart_data
        }
#  Top Repeated Customer 


    @http.route('/top/repeated/cust/chart/data', auth='public', type='json')
    def get_top_repeated_cust_chart_data(self, **kw):
        
        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae', '#ed843f', '#00c4aa',
                          '#966ca2', '#e2d65e', '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad']     
    
        data=kw['data']
        request_domain = []
        top_team_order_count=data['top_team_order_count']
        today = date.today()
        if not data.get('duration'):
            request_domain = [('request_date', '>=', today ),('request_date', '<=', today )]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    request_domain = [('user_id','=',user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    request_domain += [('customer_id','=',partner_id)]
            
            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    request_domain += [('request_date', '>=', filter_date), ('request_date', '<=', today)]


        top_repeated_customer=[]
        top_repeated_customer_chart=[]
        top_repeated_customer_repeat_time=[]
        
        top_customer_order = request.env['dev.repair.request'].search_read(request_domain, fields=['customer_id'])
        n_lines = sorted(top_customer_order, key=itemgetter('customer_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('customer_id'))
        lines = [{'customer_id': k, 'values': [x for x in v]} for k, v in groups]

        order_ids_lst=[]
        for x in lines:
            order_id_lst = []
            for id in x['values']:
                order_id_lst.append(id['id'])
            order_ids_lst.append(order_id_lst)
            order_ids_lst=sorted(order_ids_lst, key=lambda x: len(x), reverse=True)

        for line in lines:
            top_repeated_customer.append(
                {'customer': line.get('customer_id')[1], 'repeated_time': len(line.get('values'))})
        top_repeated_customer = (sorted(top_repeated_customer, key=lambda i: i['repeated_time'], reverse=True))[0:int(top_team_order_count)]
        for rep_customer_data in top_repeated_customer:
            top_repeated_customer_chart.append(rep_customer_data.get('customer'))
            top_repeated_customer_repeat_time.append(rep_customer_data.get('repeated_time'))

        top_repeated_customer_chart_data = {
            'labels': top_repeated_customer_chart,
            'datasets': [{
                'label': "Top Repeated Customer",
                'backgroundColor': all_color_list[:len(top_repeated_customer_chart)],
                'data': top_repeated_customer_repeat_time,
                'detail':order_ids_lst
            }]
        }
        return{
            'top_repeated_customer_chart_data': top_repeated_customer_chart_data
        }

# Lead list data 
    @http.route('/garage/lead/list/data', auth='public', type='json')
    def get_garage_lead_list_data(self, **kw):
        today = date.today()
        
        data = kw['data']
        garage_lead_domain = [('service_id','!=',False),('type','=','lead')]
        if not data.get('duration'):
            garage_lead_domain += [('create_date', '>=', today),('create_date', '<=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    garage_lead_domain += [('user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    garage_lead_domain += [('partner_id', '=', partner_id)]

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    garage_lead_domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]


        garage_lead_ids = request.env['crm.lead'].search_read(garage_lead_domain,fields=['name', 'partner_id','email_from','create_date',     
                                                                        'user_id'],
                                                                    order="id desc")
        print(garage_lead_ids)
        return {
            'garage_lead_ids': garage_lead_ids
        }


# Due invoice List

    @http.route('/due/invoice/list/data', auth='public', type='json')
    def get_due_invoice_list_data(self, **kw):
        today = date.today()
        
        data = kw['data']
        due_invoice_domain = [('payment_state','=','not_paid')]
        if not data.get('duration'):
            due_invoice_domain += [('invoice_date', '=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    due_invoice_domain += [('invoice_user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    due_invoice_domain += [('partner_id', '=', partner_id)]

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    due_invoice_domain += [('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]


        total_sales_id_list = request.env['project.task'].search([])
        valid_sale_order_ids = [task.sale_id.id for task in total_sales_id_list if task.sale_id]

        if valid_sale_order_ids:
            sale_order_domain = [('id', 'in', valid_sale_order_ids)]
            sale_orders = request.env['sale.order'].search(sale_order_domain)
        else:
            sale_orders = request.env['sale.order'].browse([])

        all_invoice_ids = []
        for order in sale_orders:
            all_invoice_ids += order.invoice_ids.ids
        if all_invoice_ids:
            filtered_invoice_domain = [('id', 'in', all_invoice_ids)] + due_invoice_domain
            due_invoice_ids = request.env['account.move'].search_read(
                filtered_invoice_domain,
                fields=['name', 'partner_id', 'invoice_date', 'amount_untaxed_in_currency_signed', 'state'],
                order="id desc"
            )
        else:
            due_invoice_ids = []

        return {
            'due_invoice_ids': due_invoice_ids
        }


# Paid Invoice

    @http.route('/paid/invoice/list/data', auth='public', type='json')
    def get_paid_invoice_list_data(self, **kw):
        today = date.today()

        data = kw.get('data', {})
        paid_invoice_domain = [('payment_state', '=', 'paid')]

        if not data.get('duration'):
            paid_invoice_domain += [('invoice_date', '=', today)]
        if data:
            if data['user_id']:
                if data['user_id'] != 'all':
                    user_id = int(data['user_id'])
                    paid_invoice_domain += [('invoice_user_id', '=', user_id)]
            if data['partner_id']:
                if data['partner_id'] != 'all':
                    partner_id = int(data['partner_id'])
                    paid_invoice_domain += [('partner_id', '=', partner_id)]

            if data['duration']:
                duration = data['duration']
                if duration != "all":
                    duration = int(duration)
                    filter_date = today - timedelta(days=duration)
                    paid_invoice_domain += [('invoice_date', '>=', filter_date), ('invoice_date', '<=', today)]



        total_sales_id_list = request.env['project.task'].search([])
        valid_sale_order_ids = [task.sale_id.id for task in total_sales_id_list if task.sale_id]

        if valid_sale_order_ids:
            sale_order_domain = [('id', 'in', valid_sale_order_ids)]
            sale_orders = request.env['sale.order'].search(sale_order_domain)
        else:
            sale_orders = request.env['sale.order'].browse([])

        all_invoice_ids = [inv.id for order in sale_orders for inv in order.invoice_ids]

        if all_invoice_ids:
            filtered_paid_invoice_domain = [('id', 'in', all_invoice_ids)] + paid_invoice_domain
            paid_invoice_ids = request.env['account.move'].search_read(
                filtered_paid_invoice_domain,
                fields=['name', 'partner_id', 'invoice_date', 'amount_untaxed_in_currency_signed', 'state'],
                order="id desc"
            )
        else:
            paid_invoice_ids = []

        return {
            'paid_invoice_ids': paid_invoice_ids
        }


    @http.route('/garage/filter-apply', auth='public', type='json')
    def garage_filter_apply(self, **kw):
        data = kw['data']
        user_id = data['user']
        partner_id = data['customer']
        duration = data['duration']
        result = self.get_tiles_data(user_id=user_id,partner_id=partner_id,duration=duration)
        return result
