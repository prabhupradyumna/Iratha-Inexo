# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Garage Management System | Vehicle Garage',
    'version': '19.0.1.3',
    'sequence': 1,
    'category': 'Services',
    'description':
        """
       This odoo application adds Garage Management feature into the odoo. If you are running a Garage then you can manage your customers and their job cards using this application. Customer can make repair request from website and user can create job card of that customer from that request. Create vehicle diagnosis. If required, user can purchase product from vendor in vehicle diagnosis and Create work order of customer job card. All works can be seen by the timesheets. Create sale from vehicle diagnosis and this sale order is also linked with job card. Sale order will become based on the service charge and product who need to be repaired in vehicle and Email will be sent to the customer with attachment of report when job card is done. Also send rating email to customer when the job card is done. Configure Services , Service types , Inspection , Vehicles Model and Vehicle parts. Also sent email to customer for renewal service of their's vehicle. Separate menu to see vehicle diagnosis and vehicle work orders. Various kinds of reports are provided for better understanding.
       
       Garage Management Odoo App with Job Card Estimation Requisition Vehicle Details Timesheets Checklist Instructions Auto fleet repair car repair workshop vehicle repair services fleet maintenance fleet vehicle workshop management garage management car service center machine work orders fleet repairing service auto repair shop vehicle repair industry fleet management  Management solution for workshop or autoshop or garage for all kind of vechile which include following features Online or offline jobcard request Vechile inspection and workorder Technicain work timesheets Spart part and service products estimation Quotation and RFQ or Invoices and Bills Notify manager and customer about renewal service by mail Schedule auto service remainder Message or mail from jobcards with clients Jobcard, inspection or workorder report Repair management  Autoshop management Garage management Spare parts, techincial and workshop efficency reports

    """,
    'summary': 'Garage Management Odoo App with Job Card Estimation Requisition Vehicle Details Timesheets Checklist Instructions Auto fleet repair car repair workshop vehicle repair services fleet maintenance fleet vehicle workshop management garage management car service center machine work orders fleet repairing service auto repair shop vehicle repair industry fleet management  Management solution for workshop or autoshop or garage for all kind of vechile which include following features Online or offline jobcard request Vechile inspection and workorder Technicain work timesheets Spart part and service products estimation Quotation and RFQ or Invoices and Bills Notify manager and customer about renewal service by mail Schedule auto service remainder Message or mail from jobcards with clients Jobcard, inspection or workorder report Repair management  Autoshop management Garage management Spare parts, techincial and workshop efficency reports dashboard advanced dashboard',
    'depends': ['sale_management','sale_stock','purchase','crm','fleet','project','hr_timesheet','portal','website','rating','calendar'],
    'data': [
            'security/security.xml',
            'security/ir.model.access.csv',
            'data/sequence.xml',
            'report/report_menu.xml',
            'data/mail_template.xml',
            'views/main_menu.xml',
            # 'views/website_menu.xml',
            'wizard/create_purchase.xml',
            'wizard/job_card_history.xml',
            'wizard/product_sale_history.xml',
            'views/service_views.xml',
            'views/instruction_views.xml',
            'views/team_views.xml',
            'views/product_template.xml',
            'views/repair_request_views.xml',
            'views/project_task_views.xml',
            'views/customer_portal.xml',
            'views/res_config_settings.xml',
            'views/repair_request_template.xml',
            # 'views/crm_lead.xml',
            'views/fleet_vehicle_model.xml',
            'views/fleet_service_type.xml',
            'views/inspection_template_view.xml',
            'views/job_card_analysis.xml',
            'report/repair_requst_report.xml',
            'report/job_card_history.xml',
            'report/product_sale_history_report.xml',
            'report/job_card_label_view.xml',
            'report/instruction_checklist_view.xml',
            'views/dashboard_menu.xml',
            'views/time_slot_view.xml',
            'views/minutes_of_meetings.xml',
            'portal_request/website_request_menu.xml',
            'portal_request/appointment_request_view.xml',
            'portal_request/garage_request_view.xml',
            'data/demo_data.xml',
            
        ],
            'assets': {
   'web.assets_backend': [
       'dev_garage_management/static/src/css/dashboard_new.css',
       'dev_garage_management/static/src/js/garage_anlysis_dashboard.js',
       'dev_garage_management/static/src/xml/garage_analysis_dashboard.xml',
       'dev_garage_management/static/src/js/chart_chart.js'
       
   ],

   'web.assets_frontend': [
            'dev_garage_management/static/src/js/CalendarView.js',
        ],
    
    },
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'https://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':99.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
    'pre_init_hook' :'pre_init_check',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
