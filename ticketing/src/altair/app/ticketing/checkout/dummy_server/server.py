# encoding: utf-8

import re
from base64 import b64encode, b64decode
from lxml import etree
import lxml.builder
from hmac import new as hmac_new
from decimal import Decimal
import hashlib
import urllib2
from urllib import urlencode
from datetime import datetime
from dateutil.parser import parse as parsedate
from zope.interface import Interface, implementer
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.decorator import reify
import js.bootstrap_ts
from wtforms.validators import Required
from markupsafe import Markup
from webhelpers.util import html_escape
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, OurIntegerField

from .models import (
    DummyCart,
    DummyCartedProduct,
    DummyProduct,
    )

class DummyServerApplicationException(Exception):
    pass

class OrderNotExist(DummyServerApplicationException):
    pass

class PayloadParseError(DummyServerApplicationException):
    pass

class InvalidCallbackResponseError(DummyServerApplicationException):
    pass

class IConfigurationProvider(Interface):
    def find_by_service_name(service_name):
        pass

    def find_by_service_id(service_id):
        pass

    def __iter__():
        pass

class ISerialNumberGenerator(Interface):
    def __call__(name):
        pass

@implementer(IConfigurationProvider)
class ConfigurationProvider(object):
    PREFIX = 'altair.anshin_checkout.dummy_server'

    def __init__(self, config):
        services_prefix = self.PREFIX + '.services'
        pyramid_settings = config.registry.settings
        services = re.split(ur'\s+(?:,\s+)?', pyramid_settings[services_prefix])
        settings_by_service_id = {}
        settings_by_service_name = {}
        settings_list = []
        for service in services:
            service_id = pyramid_settings['%s.%s.service_id' % (services_prefix, service)]
            signature_key = pyramid_settings['%s.%s.signature_key' % (services_prefix, service)]
            cart_confirming_url = pyramid_settings.get('%s.%s.cart_confirming_url' % (services_prefix, service), None)
            completion_notification_url = pyramid_settings.get('%s.%s.completion_notification_url' % (services_prefix, service), None)
            settings = {
                'name': service,
                'service_id': service_id,
                'signature_key': signature_key,
                'endpoints': {
                    'cart_confirming_url': cart_confirming_url,
                    'completion_notification_url': completion_notification_url,
                    }
                }
            settings_by_service_id[service_id] = settings
            settings_by_service_name[service] = settings
            settings_list.append(settings)
        self.settings_by_service_id = settings_by_service_id
        self.settings_by_service_name = settings_by_service_name
        self.settings_list = settings_list

    def find_by_service_id(self, service_id):
        return self.settings_by_service_id.get(service_id)

    def find_by_service_name(self, service_name):
        return self.settings_by_service_name.get(service_name)

    def __iter__(self):
        return iter(self.settings_list)

@implementer(ISerialNumberGenerator)
class SerialNumberGenerator(object):
    def __init__(self):
        self.serials = {}

    def __call__(self, name):
        retval = self.serials[name] = self.serials.get(name, 0) + 1
        return retval


def bad_request(message):
    return HTTPBadRequest(content_type='text/html', unicode_body=message)

def must_find(n, path):
    retval = n.find(path)
    if retval is None:
        raise PayloadParseError(u'%s does not exist' % path)
    return retval

def retrieve_item_from_tree(item_n):
    if item_n.tag != u'item':
        raise PayloadParseError(u'unexpected element %s within itemsInfo element' % item_n.tag)
    item_id_n = must_find(item_n, u'itemId')
    item_name_n = must_find(item_n, u'itemName')
    item_numbers_n = must_find(item_n, u'itemNumbers')
    item_fee_n = must_find(item_n, u'itemFee')
    try:
        item_id_str = item_id_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty itemId')
    try:
        item_name_str = item_name_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty itemName')
    try:
        item_numbers_str = item_numbers_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty itemNumbers')
    try:
        item_fee_str = item_fee_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty itemFee')
    try:
        quantity = int(item_numbers_str)
    except (TypeError, ValueError):
        raise PayloadParseError(u'invalid value for itemNumbers: %s' % item_numbers_str)
    try:
        price = Decimal(item_fee_str)
    except TypeError:
        raise PayloadParseError(u'invalid value for itemFee: %s' % item_fee_str)
    item = {
        'id': item_id_str,
        'name': item_name_str,
        'quantity': quantity,
        'price': price,
        }
    return item

def parse_order(root):
    order_cart_id_n = must_find(root, u'orderCartId')
    order_complete_url_n = must_find(root, u'orderCompleteUrl')
    order_failed_url_n = must_find(root, u'orderFailedUrl')
    order_total_fee_n = must_find(root, u'orderTotalFee')
    is_t_mode_n = must_find(root, u'isTMode')
    items_info_n = must_find(root, u'itemsInfo')

    try:
        order_cart_id_str = order_cart_id_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty orderCartId')
    try:
        order_complete_url_str = order_complete_url_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty orderCompleteUrl')
    try:
        order_failed_url_str = order_failed_url_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty orderFailedUrl')
    try:
        order_total_fee_str = order_total_fee_n.text.strip()
    except AttributeError:
        raise PayloadParseError(u'empty orderTotalFee')

    is_t_mode_str = is_t_mode_n.text.strip() if is_t_mode_n.text else u''

    try:
        total_amount = Decimal(order_total_fee_str)
    except AttributeError:
        raise PayloadParseError(u'invalid value for orderTotalFee: %s' % order_total_fee_str)

    items = [
        retrieve_item_from_tree(item_n)
        for item_n in items_info_n
        ]
    return {
        'order_cart_id': order_cart_id_str,
        'order_complete_url': order_complete_url_str,
        'order_failed_url': order_failed_url_str,
        'total_amount': total_amount,
        'test_mode': is_t_mode_str,
        'items': items,
        }

def build_payload_for_cart_confirming(order, cart_confirmation_id, openid_claimed_id):
    E = lxml.builder.E
    payload = E.cartConfirmationRequest(
        E.openId(openid_claimed_id),
        E.carts(
            E.cart(
                E.cartConfirmationId(cart_confirmation_id),
                E.orderCartId(order['order_cart_id']),
                E.orderTotalFee(unicode(order['total_amount'].quantize(0))),
                E.items(*(
                    E.item(
                        E.itemId(item['id']),
                        E.itemName(item['name']),
                        E.itemNumbers(unicode(item['quantity'])),
                        E.itemFee(unicode(item['price'].quantize(0)))
                        )
                    for item in order['items']
                    )),
                E.isTMode(order['test_mode']),
                )
            )
        )
    return payload

def parse_cart_confirming_callback_response(xml):
    if xml.tag != u'cartConfirmationResponse':
        raise PayloadParseError(u'root element must be cartConfirmationResponse')

    carts_n = xml.find('carts')
    if carts_n is None:
        raise PayloadParseError(u'missing <carts> element under cartConfirmationResponse')
    carts = []
    for cart_n in carts_n:
        if cart_n.tag != u'cart':
            raise PayloadParseError(u'unexpected element <%s> under <carts>' % cart_n.tag)
        items_n = must_find(cart_n, 'items')
        cart_confirmation_id_n = must_find(cart_n, 'cartConfirmationId')
        order_cart_id_n = must_find(cart_n, 'orderCartId')
        order_items_total_fee_n = must_find(cart_n, 'orderItemsTotalFee')
        try:
            cart_confirmation_id_str = cart_confirmation_id_n.text.strip()
        except AttributeError:
            raise PayloadParseError(u'empty cartConfirmationId')
        try:
            order_cart_id_str = order_cart_id_n.text.strip()
        except AttributeError:
            raise PayloadParseError(u'empty orderCartId')
        try:
            order_items_total_fee_str = order_items_total_fee_n.text.strip()
        except AttributeError:
            raise PayloadParseError(u'empty orderItemsTotalFee')
        try:
            total_amount = Decimal(order_items_total_fee_str)
        except AttributeError:
            raise PayloadParseError(u'invalid value for orderTotalFee: %s' % order_items_total_fee_str)

        items = [
            retrieve_item_from_tree(item)
            for item in items_n
            ]
        cart = {
            'cart_confirmation_id': cart_confirmation_id_str,
            'order_cart_id': order_cart_id_str,
            'total_fee': total_fee,
            'items': items,
            }
        carts.append(cart)
    return {
        'carts': carts,
        }
        
def build_payload_for_completion_notification(order, order_id, order_control_id, order_date, used_point, openid_claimed_id):
    E = lxml.builder.E
    payload = E.orderCompleteRequest(
        E.orderId(order_id),
        E.orderControlId(order_control_id),
        E.openId(openid_claimed_id),
        E.orderCartId(order['order_cart_id']),
        E.usedPoint(unicode(used_point.quantize(0))),
        E.orderDate(order_date.strftime('%Y-%m-%d %H:%M:%S').decode('utf-8')),
        E.orderTotalFee(unicode(order['total_amount'].quantize(0))),
        E.items(*[
            E.item(
                E.itemId(item['id']),
                E.itemName(item['name']),
                E.itemNumbers(unicode(item['quantity'])),
                E.itemFee(unicode(item['price'].quantize(0)))
                )
            for item in order['items']
            ]),
        E.isTMode(order['test_mode'])
        )
    return payload

def parse_completion_notification_callback_response(xml):
    if xml.tag != u'orderCompleteResponse':
        raise PayloadParseError(u'root element must be orderCompleteResponse')

    result_n = must_find(xml, u'result')
    complete_time_n = must_find(xml, u'completeTime')

    try:
        result = int(result_n.text.strip())
    except AttributeError:
        raise PayloadParseError(u'empty <result> element')
    except (TypeError, ValueError):
        raise PayloadParseError(u'invalid value for <result> element')

    try:
        complete_time = parsedate(complete_time_n.text.strip())
    except AttributeError:
        raise PayloadParseError(u'empty <completeTime> element')
    except ValueError:
        raise PayloadParseError(u'invalid value for <completeTime> element')
    return {
        'result': result,
        'complete_time': complete_time,
        }


def build_opener():
    return urllib2.build_opener(
        urllib2.UnknownHandler(),
        urllib2.HTTPHandler(),
        urllib2.HTTPDefaultErrorHandler(),
        urllib2.HTTPRedirectHandler(),
        urllib2.HTTPErrorProcessor()
        )

class CallbackSender(object):
    def __init__(self, serial_number_generator, opener, now, service_settings, openid_claimed_id):
        self.serial_number_generator = serial_number_generator
        self.opener = opener
        self.now = now
        self.service_settings = service_settings
        self.openid_claimed_id = openid_claimed_id

    def next_cart_confirmation_id(self):
        return '%s-%04d%02d%02d-%08d' % (
            self.service_settings['service_id'],
            self.now.year, self.now.month, self.now.day,
            self.serial_number_generator('cart_confirmation_id'),
            )

    def next_order_id(self):
        return '%s-%04d%02d%02d-%010d' % (
            self.service_settings['service_id'],
            self.now.year, self.now.month, self.now.day,
            self.serial_number_generator('order_id'),
            )

    def next_order_control_id(self):
        return 'dc-%s-%02d%02d%02d-%010d' % (
            self.service_settings['service_id'],
            self.now.year % 100, self.now.month, self.now.day,
            self.serial_number_generator('order_control_id'),
            )

    def send_cart_confirming_request(self, order):
        cart_confirming_url = self.service_settings['endpoints']['cart_confirming_url']
        if cart_confirming_url is None:
            return
        xml = build_payload_for_cart_confirming(
            order=order,
            cart_confirmation_id=self.next_cart_confirmation_id(),
            openid_claimed_id=self.openid_claimed_id
            )
        in_payload = etree.tostring(xml, encoding='utf-8', xml_declaration=True)
        req = urllib2.Request(
            cart_confirming_url,
            data=urlencode({ u'confirmId': b64encode(in_payload) })
            )
        resp = self.opener.open(req)
        try:
            out_payload = resp.read()
            if resp.code != 200:
                raise InvalidCallbackResponseError(u'endpoint returned error status: status=%s, message=%s' % (resp.code, resp.msg))
            try:
                xml = etree.fromstring(out_payload)
            except Exception as e:
                raise InvalidCallbackResponseError(u'could not parse payload as XML: %s' % e.message)
            return parse_cart_confirming_callback_response(xml)
        finally:
            resp.close()

    def send_order_completion_notification_request(self, order, used_point=Decimal(0)):
        completion_notification_url = self.service_settings['endpoints']['completion_notification_url']
        if completion_notification_url is None:
            return
        xml = build_payload_for_completion_notification(
            order=order,
            order_id=self.next_order_id(),
            order_control_id=self.next_order_control_id(),
            order_date=self.now,
            used_point=used_point,
            openid_claimed_id=self.openid_claimed_id
            )
        in_payload = etree.tostring(xml, encoding='utf-8', xml_declaration=True)
        req = urllib2.Request(
            completion_notification_url,
            data=urlencode({ u'confirmId': b64encode(in_payload) })
            )
        resp = self.opener.open(req)
        try:
            out_payload = resp.read()
            if resp.code != 200:
                raise InvalidCallbackResponseError(u'endpoint returned error status: status=%s, message=%s' % (resp.code, resp.msg))
            try:
                xml = etree.fromstring(out_payload)
            except Exception as e:
                raise InvalidCallbackResponseError(u'could not parse payload as XML: %s' % e.message)
            return parse_completion_notification_callback_response(xml)
        finally:
            resp.close()

def get_serial_number_generator(registry):
    return registry.getUtility(ISerialNumberGenerator)

def make_callback_sender(registry, service_settings, openid_claimed_id=None):
    if openid_claimed_id is None:
        openid_claimed_id = u'http://example.com/dummy-open-id'
    opener = build_opener()
    return CallbackSender(
        get_serial_number_generator(registry),
        opener,
        datetime.now(),
        service_settings,
        openid_claimed_id
        )

def get_configuration_provider(registry):
    return registry.getUtility(IConfigurationProvider)

def get_service_settings(registry, service_id):
    return get_configuration_provider(registry).find_by_service_id(service_id)

def enumerate_service_settings(registry):
    return iter(get_configuration_provider(registry))

class PaymentInfoForm(OurForm):
    openid_claimed_id = OurTextField(
        validators=[
            Required(),
            ],
        default=u'http://example.com/dummy-open-id'
        )

    used_point = OurIntegerField(
        default=u'0'
        )

class DummyCheckoutView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        js.bootstrap_ts.bootstrap.need()
        js.bootstrap_ts.bootstrap_responsive_css.need()

    def get_payload(self):
        encoded_payload = self.request.POST.get('checkout')
        if encoded_payload is None:
            raise bad_request(u'no payload given')
        sig = self.request.POST.get('sig')
        if sig is None:
            raise bad_request(u'no signature given')
        try:
            payload = b64decode(encoded_payload)
        except:
            raise bad_request(u'could not decode payload')
        try:
            xml = etree.fromstring(payload)
        except Exception as e:
            raise bad_request(u'could not parse payload as XML: %s' % e.message)

        auth_method_n = xml.find('authMethod')
        auth_method = hashlib.sha1
        if auth_method_n is not None:
            auth_method_str = auth_method_n.text
            if auth_method_str == u'1':
                auth_method = hashlib.sha1
            elif auth_method_str == u'2':
                auth_method = hashlib.md5
            else:
                raise bad_request(u'invalid authMethod value: %s' % auth_method_str)

        service_id_n = xml.find(u'serviceId')
        if service_id_n is None:
            raise bad_request(u'serviceId not provided')
        service_id = service_id_n.text
        if service_id is None:
            raise bad_request(u'serviceId not provided')

        service_settings = get_service_settings(self.request.registry, service_id)
        h = hmac_new(service_settings['signature_key'], payload, auth_method).hexdigest()
        if sig != h:
            raise bad_request(u'invalid signature')
        return xml, service_settings

    @reify
    def verb(self):
        for k in self.request.params:
            if k.startswith('do'):
                return k[2:]
        return None

    @view_config(route_name='checkout_dummy_server.stepin')
    def stepin(self):
        xml, service_settings = self.get_payload()
        self.request.session['service_settings'] = service_settings
        try:
            self.request.session['order'] = parse_order(xml)
        except PayloadParseError as e:
            raise bad_request(u'failed to parse request: %s' % e.message)

        return HTTPFound(self.request.route_path('checkout_dummy_server.index'))

    @view_config(route_name='checkout_dummy_server.index', renderer='index.mako', request_method="GET")
    def index(self):
        if 'order' not in self.request.session:
            raise OrderNotExist()
        return {
            'service_settings': self.request.session['service_settings'],
            'order': self.request.session['order'],
            'form': PaymentInfoForm(),
            }

    @view_config(route_name='checkout_dummy_server.index', renderer='index.mako', request_method="POST")
    def index_post(self):
        if 'order' not in self.request.session:
            raise OrderNotExist()
        order = self.request.session['order']
        service_settings = self.request.session['service_settings']
        f = PaymentInfoForm(self.request.POST)
        if not f.validate():
            return {
                'service_settings': service_settings,
                'order': order,
                'form': f,
                }
        openid_claimed_id = f.openid_claimed_id.data
        used_point = Decimal(f.used_point.data)
        if self.verb == 'Authorize':
            sender = make_callback_sender(self.request.registry, service_settings, openid_claimed_id)
            try:
                sender.send_cart_confirming_request(order)
                sender.send_order_completion_notification_request(order, used_point)
            except Exception as e:
                self.request.session.flash(unicode(e))
                return {
                    'service_settings': service_settings,
                    'order': order,
                    'form': f,
                    }
            del self.request.session['order']
            del self.request.session['service_settings']
            return HTTPFound(location=order['order_complete_url'])
        elif self.verb == 'AuthorizeFailure':
            del self.request.session['order']
            del self.request.session['service_settings']
            return HTTPFound(location=order['order_failed_url'])
        return HTTPFound(location=self.request.current_route_path())

    @view_config(route_name='checkout_dummy_server.diag', renderer='diag.mako')
    def diag(self):
        from altair.app.ticketing.checkout.api import Checkout, get_signer
        order = DummyCart(
            id=0,
            system_fee=Decimal(100),
            delivery_fee=Decimal(100),
            special_fee=Decimal(100),
            items=[
                DummyCartedProduct(
                    product=DummyProduct(id=1, name=u'ダミー', price=Decimal(1000)),
                    quantity=3
                    ),
                ]
            )
        payloads = []
        for service_settings in enumerate_service_settings(self.request.registry):
            co = Checkout(
                service_settings['service_id'],
                self.request.route_path('checkout_dummy_server.diag'),
                self.request.route_path('checkout_dummy_server.diag'),
                'HMAC-SHA1',
                service_settings['signature_key'],
                self.request.application_url,
                False
                )
            payload = co.create_checkout_request_xml(order).encode('utf-8')
            signer = get_signer(co.auth_method, co.secret)
            payloads.append({
                'name': service_settings['name'],
                'payload': b64encode(payload),
                'sig': signer(payload),
                })
        return {
            'payloads': payloads,
            }

    @view_config(context=OrderNotExist, renderer='error.mako')
    def _order_not_exist(self):
        return {u'summary': u'no order specified', u'detail': self.context.message}

def errors_for(request, field):
    buf = []
    buf.append(u'<ul>')
    for error in field.errors:
        buf.append(u'<li>')
        buf.append(html_escape(error))
        buf.append(u'</li>')
    buf.append(u'</ul>')
    return Markup(u''.join(buf))

class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

def register_helpers(event):
    request = event['request']
    event.update(
        h=Namespace(
            errors_for=lambda *args, **kwargs: errors_for(request, *args, **kwargs)
            )
        )


def setup_routes(config):
    config.add_route('checkout_dummy_server.stepin', '/myc/cdodl/1.0/stepin')
    config.add_route('checkout_dummy_server.diag', '/.dummy/diag/')
    config.add_route('checkout_dummy_server.index', '/.dummy/')

def setup_renderers(config):
    config.add_renderer('.mako' , 'pyramid.mako_templating.renderer_factory')

def setup_sqlalchemy(config):
    import sqlalchemy
    from .models import Base
    config.registry.sa_engine = sqlalchemy.create_engine('sqlite:///')
    config.registry.sa_base = Base
    config.registry.sa_base.metadata.drop_all(config.registry.sa_engine)
    config.registry.sa_base.metadata.create_all(config.registry.sa_engine)

def setup_session(config):
    from altair.httpsession.pyramid import PyramidSessionFactory, cookies
    from altair.httpsession.pyramid.interfaces import ISessionHTTPBackendFactory, ISessionPersistenceBackendFactory
    from altair.httpsession.inmemory import factory as inmemory_session_backend_factory
    config.registry.registerUtility(
        lambda request: cookies(request),
        ISessionHTTPBackendFactory
        )

    config.registry.registerUtility(
        lambda request: inmemory_session_backend_factory(request),
        ISessionPersistenceBackendFactory
        )
    config.set_session_factory(PyramidSessionFactory())

def setup_components(config):
    config.registry.registerUtility(ConfigurationProvider(config), IConfigurationProvider)
    config.registry.registerUtility(SerialNumberGenerator(), ISerialNumberGenerator)

def setup_helpers(config):
    config.add_subscriber(register_helpers, 'pyramid.events.BeforeRender')

def main():
    return paster_main({})

def paster_main(global_config, **local_config):
    from pyramid.config import Configurator
    settings = dict(global_config)
    settings.update(local_config)
    settings['mako.directories'] = 'altair.app.ticketing.checkout.dummy_server:templates'
    config = Configurator(settings=settings)
    config.scan('.')
    config.include("pyramid_fanstatic")
    config.include('altair.exclog')
    config.include(setup_components)
    config.include(setup_renderers)
    config.include(setup_session)
    config.include(setup_sqlalchemy)
    config.include(setup_routes)
    config.include(setup_helpers)
    return config.make_wsgi_app()
