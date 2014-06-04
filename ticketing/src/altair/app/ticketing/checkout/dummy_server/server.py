# encoding: utf-8

import re
from base64 import b64encode, b64decode
from lxml import etree
from hmac import new as hmac_new
from decimal import Decimal
import hashlib
import urllib2
import logging
from urllib import urlencode
from datetime import datetime
from zope.interface import Interface, implementer
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPOk
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

from .payload import (
    PayloadParseError,
    parse_order,
    build_payload_for_cart_confirming,
    parse_cart_confirming_callback_response,
    build_payload_for_completion_notification,
    parse_completion_notification_callback_response,
    build_settlement_response,
    parse_settlement_request,
    build_cancel_response,
    parse_cancel_request,
    build_update_response,
    parse_update_request,
    )

logger = logging.getLogger(__name__)

class DummyServerApplicationException(Exception):
    pass

class OrderNotExist(DummyServerApplicationException):
    pass

class InvalidCallbackResponseError(DummyServerApplicationException):
    pass

class ApiError(DummyServerApplicationException):
    @property
    def message(self):
        return self.args[0]

    @property
    def code(self):
        return self.args[1]

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
            access_key = pyramid_settings['%s.%s.access_key' % (services_prefix, service)]
            cart_confirming_url = pyramid_settings.get('%s.%s.cart_confirming_url' % (services_prefix, service), None)
            completion_notification_url = pyramid_settings.get('%s.%s.completion_notification_url' % (services_prefix, service), None)
            settings = {
                'name': service,
                'service_id': service_id,
                'access_key': access_key,
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
        h = hmac_new(service_settings['access_key'], payload, auth_method).hexdigest()
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
                service_settings['access_key'],
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


class DummyCheckoutApiView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_payload(self):
        self.request.content_type = 'application/x-www-form-urlencoded'
        encoded_payload = self.request.POST.get('rparam')
        if encoded_payload is None:
            raise ApiError(u'no payload given', 600)
        try:
            payload = b64decode(encoded_payload)
        except:
            raise ApiError(u'failed to decode payload', 600)
        try:
            xml = etree.fromstring(payload)
        except Exception as e:
            raise ApiError(u'failed to parse payload', 600)

        service_id_n = xml.find(u'serviceId')
        if service_id_n is None:
            raise bad_request(u'serviceId not provided')
        service_id = service_id_n.text
        if service_id is None:
            raise bad_request(u'serviceId not provided')

        access_key_n = xml.find('accessKey')
        if access_key_n is None:
            raise ApiError(u'accessKey not provided', 400)
        access_key = access_key_n.text
        if access_key is None:
            raise ApiError(u'accessKey not provided', 400)

        service_settings = get_service_settings(self.request.registry, service_id)
        if service_settings['access_key'] != access_key:
            raise ApiError(u'accessKey does not match', 400)
        return xml, service_settings

    @view_config(context=ApiError)
    def _api_error(self):
        out_xml = build_settlement_response([], 1, self.context.code)
        logger.error(self.context)
        return HTTPOk(
            body=etree.tostring(out_xml, xml_declaration=True, encoding='utf-8'),
            content_type='text/xml; charset=utf-8'
            )

    @view_config(route_name='checkout_dummy_server.api.settlement')
    def api_settlement(self):
        xml, service_settings = self.get_payload()
        try:
            settlement_req = parse_settlement_request(xml)
        except PayloadParseError as e:
            raise ApiError(e.message, 600)

        orders = settlement_req['orders']
        out_xml = build_settlement_response(orders, 0, None)
        return HTTPOk(
            body=etree.tostring(out_xml, xml_declaration=True, encoding='utf-8'),
            content_type='text/xml; charset=utf-8'
            )

    @view_config(route_name='checkout_dummy_server.api.cancel')
    def api_cancel(self):
        xml, service_settings = self.get_payload()
        try:
            settlement_req = parse_cancel_request(xml)
        except PayloadParseError as e:
            raise ApiError(e.message, 600)

        orders = settlement_req['orders']
        out_xml = build_settlement_response(orders, 0, None)
        return HTTPOk(
            body=etree.tostring(out_xml, xml_declaration=True, encoding='utf-8'),
            content_type='text/xml; charset=utf-8'
            )

    @view_config(route_name='checkout_dummy_server.api.update')
    def api_update(self):
        xml, service_settings = self.get_payload()
        try:
            settlement_req = parse_update_request(xml)
        except PayloadParseError as e:
            raise ApiError(e.message, 600)

        orders = settlement_req['orders']
        out_xml = build_update_response(orders, 0, None)
        return HTTPOk(
            body=etree.tostring(out_xml, xml_declaration=True, encoding='utf-8'),
            content_type='text/xml; charset=utf-8'
            )



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
    config.add_route('checkout_dummy_server.api.settlement', '/odrctla/fixationorder/1.0/')
    config.add_route('checkout_dummy_server.api.cancel', '/odrctla/cancelorder/1.0/')
    config.add_route('checkout_dummy_server.api.update', '/odrctla/changepayment/1.0/')
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
