# encoding: utf-8

import os
import re
from dateutil.parser import parse as parsedate
from datetime import datetime, timedelta
from urlparse import urlparse
import urllib2
import lxml.html
import json
from random import shuffle, sample, randint
from lxmlmechanize.form import encode_urlencoded_form_data
from lxmlmechanize.core import Mechanize, FORM_URLENCODE_MIME_TYPE
from ConfigParser import ConfigParser

class CartBotError(Exception):
    pass

def set_form_value(form, k, v):
    elem = form.find('.//*[@name="%s"]' % k)
    if elem.tag.lower() == 'input':
        type = elem.get('type', '').lower()
        if type in ('text', 'password', 'date', 'datetime', 'datetime-local', 'time', 'week', 'month', 'color', 'email', 'number', 'range', 'tel', 'search', 'color', 'url'):
            elem.set('value', v)
        elif type in ('radio', 'checkbox'):
            checked = False
            if isinstance(v, basestring):
                if elem.get('value') == v:
                    checked = True
            else:
                if elem.get('value') in v:
                    checked = True
            if checked:
                option.set('checked', 'checked')
            else:
                option.attrib.pop('checked', None)
    elif elem.tag.lower() == 'select':
        for option in elem.findall('.//option'):
            selected = False
            if isinstance(v, basestring):
                if option.get('value') == v:
                    selected = True
            else:
                if option.get('value') in v:
                    selected = True
            if selected:
                option.set('selected', 'selected')
            else:
                option.attrib.pop('selected', None)
    elif elem.tag == 'textarea':
        elem.tag.text = v
    else:
        raise ValueError('%s for %s' % (elem.tag, k))

class CartBot(object):
    def show_sales_segment_summary(self, sales_segment_selection):
        print 'Available sales segments'
        print '------------------------'
        for date_part, sales_segments in sales_segment_selection:
            print '* %s' % date_part
            for sales_segment in sales_segments:
                print '  id: %d' % sales_segment['id']
                print '  name: %s' % sales_segment['name']
                print '  seat_types_url: %s' % sales_segment['seat_types_url']
                print '  order_url: %s' % sales_segment['order_url']
                print '  upper_limit: %s' % sales_segment['upper_limit']
        print

    def show_sales_segment_detail(self, sales_segment_detail):
        print '  venue_name: %s' % sales_segment_detail['venue_name']
        print '  performance_name: %s' % sales_segment_detail['performance_name']
        print '  event_name: %s' % sales_segment_detail['event_name']
        print '  seat_types:'
        for seat_type in sales_segment_detail['seat_types']:
            print '  * %s' % seat_type['name']
            print '    color: %s' % seat_type['style'].get('fill', {}).get('color')
            print '    description: %s' % seat_type['description']
            print '    products_url: %s' % seat_type['products_url']

    def show_pdmp_choices(self, pdmps):
        for pdmp in pdmps:
            print '* %s - %s' % (pdmp['payment_method']['name'], pdmp['delivery_method']['name'])
            print '  payment: %(fee)s (%(fee_type)s)' % pdmp['payment_method']
            print '  delivery: %(fee)s (%(fee_type)s)' % pdmp['delivery_method']
            print '  description: %s' % pdmp['description']

    def fill_shipping_address_form(self, form):
        for k in ('last_name', 'first_name', 'last_name_kana', 'first_name_kana', 'email_1', 'email_1_confirm', 'zip', 'prefecture', 'city', 'address_1', 'address_2', 'tel_1'):
            set_form_value(form, k, self.shipping_address[k].decode('utf-8'))

    def do_secure_3d_auth(self):
        host = urlparse(self.m.location).netloc
        if host == 'acs.cafis-paynet.jp':
            form = self.m.page.root.find('.//form')
            set_form_value(form, 'Password', self.credit_card_info['secure_3d_password'])
            self.m.submit_form(form)
            location = urlparse(self.m.location)
            if location.netloc != 'acs.cafis-paynet.jp' or \
               location.path != '/kc/dispatcher.jsp':
                raise CartBotError('secure 3D authentication failure')
            form = self.m.page.root.find('.//form[@name="PaRes"]')
            self.m.submit_form(form)
        else:
            raise NotImplementedError(host)
        
    def do_payment_with_credit_card(self):
        initial_location = self.m.location
        form = self.m.page.root.find('.//form')
        for k in ('card_number', 'exp_month', 'exp_year', 'card_holder_name', 'secure_code'):
            set_form_value(form, k, self.credit_card_info[k].decode('utf-8'))
        self.m.submit_form(form)
        if self.m.location == initial_location:
            form = self.m.page.root.find('.//form')
            action = form.get('action')
            if action and urlparse(action).netloc != urlparse(initial_location).netloc:
                self.m.submit_form(form)
                self.do_secure_3d_auth()
            else:
                errors = []
                for error_list_elem in self.m.page.root.findall('.//*[@class="error-list"]'):
                    name_elem = error_list_elem.getparent().find('dt')
                    if name_elem:
                        name = name_elem.text_content()
                    else:
                        name = '?'
                    for error_elem in error_list_elem.findall('li'):
                        errors.append((name, error_elem.text.encode('utf-8')))
                raise CartBotError('Failed to authorize credit card: %s' % ' / '.join('%s: %s' % pair for pair in errors))

    def do_open_id_login(self):
        form = self.m.page.root.find('.//form[@name="LoginForm"]')
        set_form_value(form, 'u', self.credentials['username'])
        set_form_value(form, 'p', self.credentials['password'])
        self.m.submit_form(form)

    def choose_seat_type(self, sales_segment_detail):
        seat_type_choices = self.seat_type_choices_map.get(sales_segment_detail['sales_segment_id'])
        if seat_type_choices is None:
            seat_type_choices = list(sales_segment_detail['seat_types'])
            shuffle(seat_type_choices)
            self.seat_type_choices_map[sales_segment_detail['sales_segment_id']] = seat_type_choices
        if seat_type_choices:
            return seat_type_choices.pop()
        else:
            return None

    def choose_pdmp(self, sales_segment_id, pdmps):
        if not pdmps:
            return None
        pdmp_choices_made = self.pdmp_choices_map.get(sales_segment_id)
        if pdmp_choices_made is None:
            pdmp_choices_made = self.pdmp_choices_map[sales_segment_id] = set()

        choices = dict((pdmp['radio'].get('value'), pdmp) for pdmp in pdmps if u'あんしん' not in pdmp['payment_method']['name'])
        eligible_choices = set(choices.keys()).difference(pdmp_choices_made)
        if not eligible_choices:
            pdmp_choices_made.clear()
            pdmp_id = sample(choices, 1)[0]
        else:
            pdmp_id = sample(eligible_choices, 1)[0]

        pdmp_choices_made.add(pdmp_id)
        return choices[pdmp_id]

    def build_order_post_data(self, sales_segment, products_to_buy):
        data = {
            'performance_id': sales_segment['performance_id'],
            }
        for product, quantity in products_to_buy:
            data['product-%d' % product['id']] = str(quantity)
        return data

    def buy_something(self): 
        self.m.navigate(self.first_page_url)
        actual_first_page_url = urlparse(self.m.location)
        if actual_first_page_url.netloc.endswith('.id.rakuten.co.jp') and \
               actual_first_page_url.path == '/rms/nid/login':
            self.do_open_id_login()
        sales_segment_selection = None
        for script in self.m.page.root.findall('head/script'):
            if script.text:
                m = re.search('^\s*var salesSegmentsSelection = ([^\n\r]*)$', script.text, re.MULTILINE)
                if m:
                    sales_segment_selection = json.loads(m.group(1).rstrip(';'))
        if not sales_segment_selection:
            raise CartBotError('%s does not contain any sales segment info' % self.m.location)

        all_sales_segments = self.all_sales_segments
        if not all_sales_segments:
            all_sales_segments = []
            for date_part, sales_segments in sales_segment_selection:
                all_sales_segments.extend(sales_segments)

            self.all_sales_segments = all_sales_segments

            self.show_sales_segment_summary(sales_segment_selection)

        sales_segment = all_sales_segments.pop(0)
        print 'Trying to buy some products that belong to %s' % sales_segment['name']
        print 
        sales_segment_detail = json.load(self.m.opener.open(sales_segment['seat_types_url']))
        self.show_sales_segment_detail(sales_segment_detail)

        print 

        seat_type = self.choose_seat_type(sales_segment_detail)
        if not seat_type:
            print "It looks like we're done with %s" % sales_segment['name']
            return None

        product_info = json.load(self.m.opener.open(seat_type['products_url']))
        products = product_info['products']
        products_to_buy = [(product, 1) for product in sample(products, randint(1, len(products)))]
        result = json.load(self.m.opener.open(
            urllib2.Request(
                sales_segment['order_url'],
                data=encode_urlencoded_form_data(self.build_order_post_data(sales_segment_detail, products_to_buy), 'utf-8'),
                headers={ 'Content-Type': FORM_URLENCODE_MIME_TYPE }
                ))
            )
        if result['result'] == 'OK':
            print 'Items bought'
            print '------------'
            for item in result['cart']['products']:
                print '* %(name)s (%(price)s): %(quantity)d' % item
            print
        else:
            print 'Items could not be bought. Out of stock?'
            return None

        # 決済フォーム
        payment_url = result['payment_url']
        print 'Navigating to %s...' % payment_url
        self.m.navigate(payment_url)

        pdmps = []
        form = self.m.page.root.find('.//form')
        pdmp_elems = form.xpath('..//*[@class="settlementPayBox"]//*[@class="settlementPayRadio"]/..')
        for pdmp_elem in pdmp_elems:
            tmp = pdmp_elem.findall('.//dl')
            if len(tmp) != 2:
                continue
            payment_method_info, delivery_method_info = tmp
            payment_method_desc = payment_method_info.find('dd')
            delivery_method_desc = delivery_method_info.find('dd')
            radio = pdmp_elem.find('*/input[@type="radio"]')
            pdmps.append(dict(
                radio=radio,
                payment_method=dict(
                    name=payment_method_info.find('dt').text,
                    fee=payment_method_desc.find('*[@class="paymentFee"]').text,
                    fee_type=(payment_method_desc.find('*[@class="paymentFeeType"]').text or "").lstrip('(').rstrip(')')
                    ),
                delivery_method=dict(
                    name=delivery_method_info.find('dt').text,
                    fee=delivery_method_desc.find('*[@class="deliveryFee"]').text,
                    fee_type=(delivery_method_desc.find('*[@class="deliveryFeeType"]').text or "").lstrip('(').rstrip(')')
                    ),
                description=(pdmp_elem.find('.//dl/dd').text or '').strip()
                ))

        print 'Available payment-delivery-method-pairs'
        print '---------------------------------------'
        self.show_pdmp_choices(pdmps)
        print

        pdmp = self.choose_pdmp(sales_segment['id'], pdmps)
        if pdmp is None:
            print "No applicable PDMP for %s" % sales_segment['name']
            return None


        print 'Selected payment-delivery-method-pair'
        print '-------------------------------------'
        self.show_pdmp_choices([pdmp])
        print

        pdmp['radio'].set('checked', 'checked')
        self.fill_shipping_address_form(form)

        self.m.submit_form(form)

        # 確認ページ
        path = urlparse(self.m.location).path
        if path == urlparse(payment_url).path:
            raise CartBotError('Failed to proceed checkout: %s' % (self.m.page.root.find('.//*[@class="error"]').text.encode('utf-8')))
        elif path == '/cart/payment/3d':
            self.do_payment_with_credit_card()
        elif path != '/cart/confirm':
            raise NotImplementedError(self.m.location)

        form = self.m.page.root.find('.//form')
        self.m.submit_form(form, submit=form.find('.//input[@id="btn-complete"]'))
        path = urlparse(self.m.location).path
        if path != '/cart/completed':
            raise CartBotError('Checkout failure')

        order_no = self.m.page.root.find('.//*[@class="confirmBox"][1]//*[@class="confirm-message"]').text_content().strip()
        print 'Checkout successful: order_no=%s' % order_no
        return order_no

    def __init__(self, url, credentials, shipping_address, credit_card_info):
        self.m = Mechanize()
        self.credentials = credentials
        self.shipping_address = shipping_address
        self.credit_card_info = credit_card_info
        self.first_page_url = url
        self.all_sales_segments = None
        self.seat_type_choices_map = {}
        self.pdmp_choices_map = {}
