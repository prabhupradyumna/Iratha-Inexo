# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from odoo.tools import groupby as groupbyelem
from operator import itemgetter
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv.expression import OR
import werkzeug
from odoo.tools.misc import get_lang


class Rating(http.Controller):

    @http.route('/rate/<string:token>/<int:rate>', type='http', auth="public", website=True)
    def action_open_rating(self, token, rate, **kwargs):
        if rate not in (1, 3, 5):
            raise ValueError(_("Incorrect rating: should be 1, 3 or 5 (received %d)"), rate)

        rating, record_sudo = self._get_rating_and_record(token)
        record_sudo.rating_apply(
            rate,
            rating=rating,
            feedback=_('Customer rated “%s”.', record_sudo.display_name),
            subtype_xmlid=None,
            notify_delay_send=True,
        )

        lang = rating.partner_id.lang or get_lang(request.env).code
        return request.env['ir.ui.view'].with_context(lang=lang)._render_template('rating.rating_external_page_submit', {
            'rating': rating,
            'token': token,
            'rate_names': {
                5: _("Satisfied"),
                3: _("Okay"),
                1: _("Dissatisfied"),
            },
            'rate': rate,
        })

    def _get_rating_and_record(self, token):
        rating_sudo = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
        if not rating_sudo:
            raise werkzeug.exceptions.NotFound()

        record_sudo = request.env[rating_sudo.res_model].sudo().browse(rating_sudo.res_id)
        if not record_sudo.exists():
            raise werkzeug.exceptions.NotFound()
        return rating_sudo, record_sudo


class CustomerPortal(CustomerPortal):

        
    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortal, self)._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'repair_request' in counters:
            repair_pool = request.env['dev.repair.request'].sudo()
            request_count = repair_pool.search_count([
		        ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
		        ('state', 'not in', ['cancel'])
		    ])
            values.update({
		        'repair_request': request_count,
		    })
        return values
        
    
    @http.route(['/my/job_card', '/my/job_card/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_repair_request(self, page=1, date_begin=None, date_end=None, sortby=None,filterby=None,search=None,search_in='content', groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        repair_pool = request.env['dev.repair.request'].sudo()

        today = fields.Date.today()
        this_week_end_date = fields.Date.to_string(fields.Date.from_string(today) + datetime.timedelta(days=7))
        week_ago = datetime.datetime.today() - datetime.timedelta(days=7)
        month_ago = (datetime.datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S')
        starting_of_year = datetime.datetime.now().date().replace(month=1, day=1)    
        ending_of_year = datetime.datetime.now().date().replace(month=12, day=31)

        def sd(date):
            return fields.Datetime.to_string(date)
        def previous_week_range(date):
            start_date = date + datetime.timedelta(-date.weekday(), weeks=-1)
            end_date = date + datetime.timedelta(-date.weekday() - 1)
            return {'start_date':start_date.strftime('%Y-%m-%d %H:%M:%S'), 'end_date':end_date.strftime('%Y-%m-%d %H:%M:%S')}

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [('request_date', '>=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 00:00:00')),('request_date', '<=', datetime.datetime.strftime(date.today(),'%Y-%m-%d 23:59:59'))]},
            'yesterday':{'label': _('Yesterday'), 'domain': [('request_date', '>=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 00:00:00')),('request_date', '<=', datetime.datetime.strftime(date.today() - datetime.timedelta(days=1),'%Y-%m-%d 23:59:59'))]},
            'week': {'label': _('This Week'),
                     'domain': [('request_date', '>=', sd(datetime.datetime.today() + relativedelta(days=-today.weekday()))), ('request_date', '<=', this_week_end_date)]},
            'last_seven_days':{'label':_('Last 7 Days'),
                         'domain': [('request_date', '>=', sd(week_ago)), ('request_date', '<=', sd(datetime.datetime.today()))]},
            'last_week':{'label':_('Last Week'),
                         'domain': [('request_date', '>=', previous_week_range(datetime.datetime.today()).get('start_date')), ('request_date', '<=', previous_week_range(datetime.datetime.today()).get('end_date'))]},
            
            'last_month':{'label':_('Last 30 Days'),
                         'domain': [('request_date', '>=', month_ago), ('request_date', '<=', sd(datetime.datetime.today()))]},
            'month':{'label': _('This Month'),
                    'domain': [
                       ("request_date", ">=", sd(today.replace(day=1))),
                       ("request_date", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))
                    ]
                },
            'year':{'label': _('This Year'),
                    'domain': [
                       ("request_date", ">=", sd(starting_of_year)),
                       ("request_date", "<=", sd(ending_of_year)),
                    ]
                }
        }


        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'not in', ['cancel'])
        ]

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name desc'},
            'date': {'label': _('Request Date'), 'order': 'request_date desc'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('All')},
            'product_id': {'input': 'session', 'label': _('Vehicle')},
			'state': {'input': 'state', 'label': _('State')},
        }

        if not filterby:
        	filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        # default sortby order
        if not sortby:
            sortby = 'name'

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # count for pager
        repair_count = repair_pool.search_count(domain)
        # make pager

        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Number')},
            'product_id': {'input': 'product_id', 'label': _('Search in Vehicle')},
            'vehicle_number': {'input': 'vehicle_number', 'label': _('Search in Vehicle Number')},
            'company_id': {'input': 'company_id', 'label': _('Search in Company')},
            'state': {'input': 'state', 'label': _('Search in State')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
                       
        # search
        if not search and search_in:
                search_in = 'name'
        if search and search_in:
                search_domain = []
                if search_in in ('name'):
                        search_domain = [('name', 'ilike', search)]
                if search_in in ('vehicle_number'):
                        search_domain = [('vehicle_number', 'ilike', search)]
                if search_in in ('product_id'):
                        search_domain = [('product_id', 'ilike', search)]
                if search_in in ('company_id'):
                        search_domain = [('company_id', 'ilike', search)]
                if search_in in ('state'):
                        search_domain = [('state', 'ilike', search)]
                if search_in in ('all'):
                        search_domain = ['|','|','|','|',('name', 'ilike', search),('vehicle_number', 'ilike', search),('product_id', 'ilike', search),
		                        ('company_id', 'ilike', search),('state', 'ilike', search)]
                domain += search_domain
		
        pager = portal_pager(
            url="/my/job_card",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby , 'search_in':search_in, 'search':search},
            total=repair_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        repair = repair_pool.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_repair_history'] = repair.ids[:100]
	
        if groupby == 'product_id':
            grouped_repair = [request.env['dev.repair.request'].concat(*g) for k, g in groupbyelem(repair, itemgetter('product_id'))]
        elif groupby == 'state':
            grouped_repair = [request.env['dev.repair.request'].sudo().concat(*g) for k, g in groupbyelem(repair, itemgetter('state'))]
        else:
            grouped_repair = [repair]

        values.update({
            'date': date_begin,
            'repair': repair.sudo(),
            'page_name': 'repair',
            'pager': pager,
            'default_url': '/my/job_card',
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,	
            'grouped_repairs': grouped_repair,
            'searchbar_groupby':searchbar_groupby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'filterby':filterby,
            'repair_request':False,
        })
        return request.render("dev_garage_management.portal_my_repair_request", values)
    
    @http.route(['/my/job_card/<int:order_id>'], type='http', auth="public", website=True)
    def portal_repair_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            repair_sudo = self._document_check_access('dev.repair.request', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=repair_sudo, report_type=report_type, report_ref='dev_garage_management.menu_machine_repair_request', download=download)
        
        if request.env.user.share and access_token:
            # If a public/portal user accesses the order with the access token
            # Log a note on the chatter.
            today = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_repair_%s' % repair_sudo.id)
            if repair_sudo != today:
                # store the date as a string in the session to allow serialization
                request.session['view_repair_%s' % repair_sudo.id] = today
                context = {'lang': repair_sudo.user_id.partner_id.lang or repair_sudo.company_id.partner_id.lang}
                author = repair_sudo.partner_id if request.env.user._is_public() else request.env.user.partner_id
                msg = _('Order viewed by customer %s', author.name)
                del context
                repair_sudo.message_post(
                    author_id=author.id,
                    body=msg,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )        
            
            
        values = {
            'repair': repair_sudo,
            'repair_request':repair_sudo,
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': repair_sudo.customer_id.id,
            'report_type': 'html',
            'p_name': repair_sudo.name,
        }
        
        
        if repair_sudo.company_id:
            values['res_company'] = repair_sudo.company_id
        if repair_sudo.state not in ('cancel'):
            history = request.session.get('my_repair_history', [])
        else:
            history = request.session.get('my_repair_history', [])
            
        values.update(get_records_pager(history, repair_sudo))
        return request.render('dev_garage_management.repair_portal_template', values)
    
    
