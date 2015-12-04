# encoding: utf-8
import time
import os
import re
from dateutil.parser import parse as parsedate
from datetime import datetime, timedelta
from urlparse import urlparse, urlunparse
import urllib2
import lxml.html
import json
from random import shuffle, sample, randint, choice
from lxmlmechanize.form import encode_urlencoded_form_data
from lxmlmechanize.core import Mechanize, FORM_URLENCODE_MIME_TYPE
from lxmlmechanize.urllib2ext.auth import KeyChain, KeyChainBackedAuthHandler, Credentials
from cookielib import CookieJar

class CartBotError(Exception):
    pass


def strip_path_part(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url[0], parsed_url[1], '', parsed_url[3], parsed_url[4], parsed_url[5]))

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
    Mechanize = Mechanize

    def print_(self, *msgs):
        print(u' '.join(msgs))

    def show_sales_segment_summary(self, sales_segment_selection):
        self.print_(u'Available sales segments')
        self.print_(u'------------------------')
        for date_part, sales_segments in sales_segment_selection:
            self.print_(u'* %s' % date_part)
            for sales_segment in sales_segments:
                self.print_(u'  id: %d' % sales_segment['id'])
                self.print_(u'  name: %s' % sales_segment['name'])
                self.print_(u'  seat_types_url: %s' % sales_segment['seat_types_url'])
                self.print_(u'  order_url: %s' % sales_segment['order_url'])
        self.print_()

    def show_sales_segment_detail(self, sales_segment_detail):
        self.print_(u'  venue_name: %s' % sales_segment_detail['venue_name'])
        self.print_(u'  performance_name: %s' % sales_segment_detail['performance_name'])
        self.print_(u'  event_name: %s' % sales_segment_detail['event_name'])
        self.print_(u'  seat_types:')
        for seat_type in sales_segment_detail['seat_types']:
            self.print_(u'  * %s' % seat_type['name'])
            self.print_(u'    color: %s' % seat_type['style'].get('fill', {}).get('color'))
            self.print_(u'    description: %s' % seat_type['description'])
            self.print_(u'    products_url: %s' % seat_type['products_url'])

    def show_pdmp_choices(self, pdmps):
        for pdmp in pdmps:
            self.print_(u'* %s - %s' % (pdmp['payment_method']['name'], pdmp['delivery_method']['name']))
            self.print_(u'  payment: %(fee)s (%(fee_type)s)' % pdmp['payment_method'])
            self.print_(u'  delivery: %(fee)s (%(fee_type)s)' % pdmp['delivery_method'])
            self.print_(u'  description: %s' % pdmp['description'])

    def fill_shipping_address_form(self, form):
        for k in ('last_name', 'first_name', 'last_name_kana', 'first_name_kana', 'email_1', 'email_1_confirm', 'zip', 'prefecture', 'city', 'address_1', 'address_2', 'tel_1'):
            set_form_value(form, k, self.shipping_address[k])

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
        form = self.m.page.root.xpath('.//form[@action!="/cart/logout"]')[0]
        for k in ('card_number', 'exp_month', 'exp_year', 'card_holder_name', 'secure_code'):
            set_form_value(form, k, self.credit_card_info[k])
        self.m.submit_form(form)
        if self.m.location == initial_location:
            form = self.m.page.root.xpath('.//form[@action!="/cart/logout"]')[0]
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
        if self.rakuten_auth_credentials is None:
            raise CartBotError('No Rakuten auth credentials provided')
        form = self.m.page.root.find('.//form[@name="LoginForm"]')
        set_form_value(form, 'u', self.rakuten_auth_credentials['username'])
        set_form_value(form, 'p', self.rakuten_auth_credentials['password'])
        self.m.submit_form(form)

    def do_fc_auth_nonguest_login(self):
        if self.fc_auth_credentials is None:
            raise CartBotError('No fc_auth credentials provided')
        form = self.m.page.root.xpath('.//form[substring(@action,string-length(@action)-5)="/login"]')[0]
        set_form_value(form, 'username', self.fc_auth_credentials['username'])
        set_form_value(form, 'password', self.fc_auth_credentials['password'])
        self.m.submit_form(form)

    def do_fc_auth_guest_login(self):
        form = self.m.page.root.xpath('.//form[substring(@action,string-length(@action)-5)="/guest"]')[0]
        self.m.submit_form(form)

    def do_fc_auth_login(self):
        if self.fc_auth_credentials is not None:
            self.do_fc_auth_nonguest_login()
        else:
            self.do_fc_auth_guest_login()

    def do_extauth_open_id_login(self):
        if self.rakuten_auth_credentials is None:
            raise CartBotError('No Rakuten auth credentials provided')
        a = self.m.page.root.xpath('.//*[@id="rakulogin"]//*[local-name()="a" and contains(@class,"btnA")]')[0]
        self.m.navigate(a.get('href'))
        self.do_open_id_login()
        memberships = {
            a.xpath('*[@class="member_kind"]')[0].text: a
            for a in self.m.page.root.xpath('.//*[@class="statusBox"]//*[local-name()="ul" and contains(@class,"statusList")]/*[local-name()="li"]/*[local-name()="a"]')
            }
        if len(memberships) == 1:
            membership = next(iter(memberships.values()))
        else:
            if self.extauth_credentials is None:
                raise CartBotError('No extauth settings provided')
            membership = memberships[self.extauth_credentials['member_kind']]
        self.m.navigate(membership.get('href'))

    def do_rsp_form(self):
        form = self.m.page.root.xpath('.//form[@action!="/cart/logout"]')[0]
        self.m.submit_form(form)

    def choose_seat_type(self, sales_segment_detail):
        seat_type_choices = self.seat_type_choices_map.get(sales_segment_detail['sales_segment_id'])
        if seat_type_choices is None:
            seat_type_choices = list(sales_segment_detail['seat_types'])
            shuffle(seat_type_choices)
            self.seat_type_choices_map[sales_segment_detail['sales_segment_id']] = seat_type_choices

        if seat_type_choices:
            while seat_type_choices:
                retval = seat_type_choices.pop()
                # 在庫がないseat_typeは選択しない
                for retrieved_seat_type_info in sales_segment_detail['seat_types']:
                    if retrieved_seat_type_info['name'] == retval['name']:
                        if retrieved_seat_type_info['availability_text'] != u'\u00d7':
                            return retval
        return None

    def choose_pdmp(self, sales_segment_id, pdmps):
        if not pdmps:
            return None
        pdmp_choices_made = self.pdmp_choices_map.get(sales_segment_id)
        if pdmp_choices_made is None:
            pdmp_choices_made = self.pdmp_choices_map[sales_segment_id] = set()

        choices = dict((pdmp['radio'].get('value'), pdmp) for pdmp in pdmps if u'楽天ID決済' not in pdmp['payment_method']['name'])
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
        self.print_('buy something start')
        self.m.navigate(self.first_page_url)
        #self.wait()
        while True:
            actual_first_page_url = urlparse(self.m.location)
            if re.match("^/cart/fc/.*/login", actual_first_page_url.path) is not None:
                self.do_fc_auth_login()
            elif re.match("^/extauth", actual_first_page_url.path) is not None:
                self.do_extauth_open_id_login()
                break
            elif actual_first_page_url.netloc.endswith('.id.rakuten.co.jp') and \
                   actual_first_page_url.path == '/rms/nid/login':
                self.do_open_id_login()
            else:
                break
        #self.wait()
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

        #sales_segment = all_sales_segments.pop(0) # why use a first element.
        sales_segment = choice(all_sales_segments)

        self.print_(u'Trying to buy some products that belong to %s' % sales_segment['name'])
        self.print_()

        req = urllib2.Request(sales_segment['seat_types_url'])
        req.add_header("X-requested-with", "XMLHttpRequest")
        sales_segment_detail = json.load(self.m.create_loader(req)())
        self.show_sales_segment_detail(sales_segment_detail)
        #self.wait()
        self.print_()

        seat_type = self.choose_seat_type(sales_segment_detail)
        if not seat_type:
            self.print_(u"It looks like we're done with %s" % sales_segment['name'])
            return None

        req = urllib2.Request(seat_type['products_url'])
        req.add_header("X-requested-with", "XMLHttpRequest")
        product_info = json.load(self.m.create_loader(req)())
        products = product_info['products']
        products_to_buy = [(product, 1) for product in sample(products, randint(1, len(products)))]

        # dummy request
        req = urllib2.Request(seat_type['seats_url'])
        req.add_header("X-requested-with", "XMLHttpRequest")
        seats_info = json.load(self.m.create_loader(req)())
        self.print_(u'seats_info -> %s' % seats_info)

        url = sales_segment['order_url']
        data = self.build_order_post_data(sales_segment_detail, products_to_buy)
        payload = encode_urlencoded_form_data(data, 'utf-8')
        headers={'Content-Type': FORM_URLENCODE_MIME_TYPE,
                 'X-Requested-With': 'XMLHttpRequest',
                 }
        req = urllib2.Request(url, payload, headers=headers)
        loader = self.m.create_loader(req)
        json_data = loader()
        result = json.load(json_data)

        """
        result = json.load(
            self.m.create_loader(
                urllib2.Request(
                    sales_segment['order_url'],
                    data=encode_urlencoded_form_data(self.build_order_post_data(sales_segment_detail, products_to_buy), 'utf-8'),
                    headers={
                        'Content-Type': FORM_URLENCODE_MIME_TYPE,
                        'X-Requested-With': 'XMLHttpRequest',
                        }
                    )
                )()
            )
        """

        if result['result'] == 'OK':
            self.print_(u'Items bought')
            self.print_(u'------------')
            for item in result['cart']['products']:
                self.print_(u'* %(name)s (%(price)s): %(quantity)d' % item)
            self.print_()
        else:
            self.print_(u'Items could not be bought. Reason: %s' % result['reason'])
            return None
        self.wait()
        # 決済フォーム
        payment_url = result['payment_url']
        self.print_(u'Navigating to %s...' % payment_url)
        self.m.navigate(payment_url)

        pdmps = []
        form = self.m.page.root.find('.//form[@name="form1"]')
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

        self.print_(u'Available payment-delivery-method-pairs')
        self.print_(u'---------------------------------------')
        self.show_pdmp_choices(pdmps)
        self.print_()

        self.wait()
        pdmp = self.choose_pdmp(sales_segment['id'], pdmps)
        if pdmp is None:
            self.print_(u"No applicable PDMP for %s" % sales_segment['name'])
            return None


        self.print_(u'Selected payment-delivery-method-pair')
        self.print_(u'-------------------------------------')
        self.show_pdmp_choices([pdmp])
        self.print_()

        pdmp['radio'].set('checked', 'checked')
        self.fill_shipping_address_form(form)

        self.m.submit_form(form)
        self.wait()
        path = urlparse(self.m.location).path
        if path == '/cart/rsp':
            self.do_rsp_form()

        # 確認ページ
        path = urlparse(self.m.location).path
        if path == urlparse(payment_url).path:
            try:
                raise CartBotError('Failed to proceed checkout: %s' % (self.m.page.root.find('.//*[@class="error"]').text.encode('utf-8')))
            except CartBotError:
                raise
            except Exception as e:
                error = self.m.page.root.find('.//*[@id="main"]').text_content().strip()
                raise CartBotError('Failed to complete an order: %s' % error.encode('utf-8'))
        elif path == '/cart/payment/3d':
            self.do_payment_with_credit_card()
        elif path != '/cart/confirm':
            raise NotImplementedError(self.m.location)

        if randint(0, 100) <= self.fail_percent:
            self.print_(u'Operation was stopped!! (Fail Percent)')
            return None

        self.wait()
        form = self.m.page.root.find('.//form[@id="form1"]')
        self.m.submit_form(form, submit=form.find('.//input[@id="btn-complete"]'))
        path = urlparse(self.m.location).path
        if path != '/cart/completed':
            raise CartBotError('Checkout failure')
        self.wait()
        confirm_message = self.m.page.root.xpath('.//*[@class="confirmBox"][1]//*[@class="confirm-message"]')
        if not confirm_message:
            error = self.m.page.root.find('.//*[@id="main"]').text_content().strip()
            raise CartBotError('Failed to complete an order: %s' % error.encode('utf-8'))

        order_no = confirm_message[0].text_content().strip()
        self.print_(u'Checkout successful: order_no=%s' % order_no)
        return order_no

    def wait(self):
        time.sleep(self._sleep_sec)

    def __init__(self, url, shipping_address, credit_card_info, rakuten_auth_credentials=None,
                 fc_auth_credentials=None, extauth_credentials=None, http_auth_credentials=None, cookiejar=None, sleep_sec=0, fail_percent=0):
        keychain = KeyChain()

        if cookiejar is None:
            cookiejar = CookieJar()

        if http_auth_credentials:
            keychain.add(Credentials(strip_path_part(url), http_auth_credentials.get('realm', None), http_auth_credentials['user'], http_auth_credentials['password']))
        opener = urllib2.build_opener(
            urllib2.ProxyHandler(),
            KeyChainBackedAuthHandler(keychain),
            urllib2.HTTPCookieProcessor(cookiejar))

        self.m = self.Mechanize(opener=opener)
        self.shipping_address = shipping_address
        self.credit_card_info = credit_card_info
        self.first_page_url = url
        self.all_sales_segments = None
        self.rakuten_auth_credentials = rakuten_auth_credentials
        self.fc_auth_credentials = fc_auth_credentials
        self.extauth_credentials = extauth_credentials
        self.seat_type_choices_map = {}
        self.pdmp_choices_map = {}
        self._sleep_sec = float(sleep_sec)
        self.fail_percent = fail_percent
