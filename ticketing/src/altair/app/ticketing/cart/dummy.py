# -*- coding:utf-8 -*-
import logging
from functools import wraps
import mock
from datetime import datetime
from pyramid.decorator import reify
from pyramid.response import Response
from mako.template import Template
from zope.interface import implementer
from altair.pyramid_dynamic_renderer import RendererHelperProxy, RequestSwitchingRendererHelperFactory
from altair.app.ticketing.mailmags import models as mailmag_models
from .request import ENV_ORGANIZATION_ID_KEY
from .interfaces import ICartResource

logger = logging.getLogger()


def includeme(config):
    default_package = config.registry.__name__

    def get_template_path_for_dummy(view_context, path):
        """cart/dummy用のget_template_path
        """
        from altair.app.ticketing.core.models import Organization
        organization_id = None
        try:
            organization_id = int(view_context.request.GET.get('organization_id', None))
        except (TypeError, ValueError):
            pass

        organization_short_name = "__default__"
        if organization_id is not None:
            organization = Organization \
                .query \
                .filter(Organization.id == organization_id) \
                .first()
            if organization:
                organization_short_name = organization.short_name
        membership = view_context.membership or "__default__"
        package_or_path, colon, _path = path.partition(':')
        if not colon:
            package = default_package
            path = package_or_path
        else:
            package = package_or_path
            path = _path
        return '%(package)s:templates/%(organization_short_name)s/%(ua_type)s/%(path)s' % dict(
            package=package,
            organization_short_name=organization_short_name,
            membership=membership,
            ua_type=view_context.ua_type,
            path=path)

    # cart/dummy用selectable_rendererで使用するrenderer_helperのfactoryクラス(callable)
    selectable_renderer_helper_factory_for_dummy = RequestSwitchingRendererHelperFactory(
        fallback_renderer='notfound.html',
        name_builder=lambda name, view_context, request: get_template_path_for_dummy(view_context, name),
        view_context_factory=lambda name, package, registry, request, **kwargs: request.view_context
        )


    def selectable_renderer_for_dummy(name):
        """cart/dummy用selectable_renderer

        Organizationの取得方法が通常のselectable_rendererと異なる
        (subdomainから取得せずurlパラメータから取得する)
        """
        return RendererHelperProxy(
            selectable_renderer_helper_factory_for_dummy,
            name,
            )

    config.add_route("dummy.cart.index", "/dummy", factory=DummyCartResource)
    config.add_view(index_view, route_name="dummy.cart.index")

    # payment
    config.add_route("dummy.cart.payment", "/dummy/payment", factory=DummyCartResource)
    config.add_view(payment_view, route_name='dummy.cart.payment', request_method="GET", 
                    renderer=selectable_renderer_for_dummy("payment.html"))
    config.add_view(payment_view, route_name='dummy.cart.payment', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET",
                    renderer=selectable_renderer_for_dummy("payment.html"))
    config.add_view(payment_view, route_name='dummy.cart.payment', request_type='altair.mobile.interfaces.ISmartphoneRequest', request_method="GET",
                    renderer=selectable_renderer_for_dummy("payment.html"))

    # confirm
    config.add_route("dummy.payment.confirm", "/dummy/confirm", factory=DummyCartResource)
    config.add_view(confirm_view, route_name='dummy.payment.confirm', request_method="GET",
                    renderer=selectable_renderer_for_dummy("confirm.html"))
    config.add_view(confirm_view, route_name='dummy.payment.confirm', request_type='altair.mobile.interfaces.IMobileRequest',
                    request_method="GET", renderer=selectable_renderer_for_dummy("confirm.html"))
    config.add_view(confirm_view, route_name='dummy.payment.confirm', request_type='altair.mobile.interfaces.ISmartphoneRequest',
                    request_method="GET", renderer=selectable_renderer_for_dummy("confirm.html"))

    # complete
    config.add_route("dummy.payment.complete", "/dummy/complete", factory=DummyCartResource)
    config.add_view(complete_view, route_name='dummy.payment.complete',
                    request_method="GET", renderer=selectable_renderer_for_dummy("completion.html"))
    config.add_view(complete_view, route_name='dummy.payment.complete', request_type='altair.mobile.interfaces.IMobileRequest',
                    request_method="GET", renderer=selectable_renderer_for_dummy("completion.html"))
    config.add_view(complete_view, route_name='dummy.payment.complete', request_type='altair.mobile.interfaces.ISmartphoneRequest',
                    request_method="GET", renderer=selectable_renderer_for_dummy("completion.html"))

    # timeout
    config.add_route("dummy.timeout", "/dummy/timeout", factory=DummyCartResource)
    config.add_view(timeout_view, route_name="dummy.timeout", renderer=selectable_renderer_for_dummy("errors/timeout.html"))

    # not found
    config.add_route("dummy.notfound", "/dummy/notfound", factory=DummyCartResource)
    config.add_view(notfound_view, route_name="dummy.notfound", renderer=selectable_renderer_for_dummy("errors/notfound.html"))
    config.add_view(notfound_view, route_name="dummy.notfound", request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer=selectable_renderer_for_dummy("errors/notfound.html"))


class DummyVenue(object):
    name = "venue"


class DummyEvent(object):
    id = 4
    title = "event"
    venue = DummyVenue()


class DummyPerformance(object):
    id = 1111
    name = "Hey"
    event = DummyEvent()
    venue = DummyVenue()

    def __init__(self):
        self.start_on = self.end_on = datetime.now()

class DummyPaymentPlugin(object):
    def __init__(self, id):
        self.id = id

class DummyDeliveryPlugin(object):
    def __init__(self, id):
        self.id = id

class DummyPaymentMethod(object):
    def __init__(self, payment_plugin_id):
        self.payment_plugin_id = payment_plugin_id
        self.payment_plugin = DummyPaymentPlugin(payment_plugin_id)


class DummyDeliveryMethod(object):
    def __init__(self, delivery_plugin_id):
        self.delivery_plugin_id = delivery_plugin_id
        self.delivery_plugin = DummyDeliveryPlugin(delivery_plugin_id)


class DummyPaymentDeliveryMethodPair(object):
    payment_method = DummyPaymentMethod(1)
    delivery_method = DummyDeliveryMethod(1)


class DummyShippingAddress(object):
    last_name = u'姓'
    first_name = u'名'
    last_name_kana = u'セイ'
    first_name_kana = u'メイ'
    zip = u'141-0031'
    prefecture = u'東京都'
    city = u'品川区'
    address_1 = u'西五反田7-1-9'
    address_2 = u'五反田HSビル7F'
    tel_1 = u'050-5817-2234'
    tel_2 = u'050-5817-2234'
    email_1 = u'dev+1@ticketstar.jp'
    email_2 = u'dev+2@ticketstar.jp'

dummy_payment_delivery_method_pair = DummyPaymentDeliveryMethodPair()
dummy_shipping_address = DummyShippingAddress()

class DummyCart(object):
    items = []
    products = []
    order_no = 'DUMMY_ORDER_'
    transaction_fee = 100
    system_fee = 200
    delivery_fee = 300
    special_fee = 400
    special_fee_name = u'★特別手数料★'
    total_amount = 500
    payment_delivery_pair = dummy_payment_delivery_method_pair
    shipping_address = dummy_shipping_address
   
    def __init__(self, performance):
        self.performance = performance

    @property
    def carted_products(self):
        return self.items


class DummyOrder(object):
    items = []
    products = []
    order_no = 'DUMMY_ORDER_'
    transaction_fee = 100
    system_fee = 200
    delivery_fee = 300
    special_fee = 400
    special_fee_name = u'★特別手数料★'
    total_amount = 500
    payment_delivery_pair = dummy_payment_delivery_method_pair
    shipping_address = dummy_shipping_address

    def __init__(self, performance):
        self.performance = performance

    @property
    def performance_id(self):
        return self.performance.id

    @property
    def ordered_products(self):
        return self.items

    def get_order_attribute_pair_pairs(self, request):
        return [
            (
                (u'key', u'value'),
                (u'キー', u'値')
                )
            ]

class DummyCartSetting(object):
    name = u'設定名称'
    type = 'standard'
    performance_selector = u'date';
    performance_selector_label1_override = u'絞り込みラベル1'
    performance_selector_label2_override = u'絞り込みラベル2'
    default_prefecture = u'宮城県'
    flavors = {}
    title = u'タイトル'
    fc_kind_title = u'タイトル'
    fc_name = u'FC名'
    contact_url = u'http://example.com/'
    contact_url_mobile = u'http://example.com/mobile/'
    contact_tel = u'tel:000'
    contact_office_hours = u'毎日24時間'
    contact_name = u'contact'
    mobile_marker_color = u'#880000'
    mobile_required_marker_color = u'#880000'
    mobile_header_background_color = u'#000088'
    fc_announce_page_url = u'http://example.com/FC'
    fc_announce_page_url_mobile = u'http://eaxmple/com/FC/mobile'
    fc_announce_page_title = u'FC'
    privacy_policy_page_url = u'http://example.com/privacy/'
    privacy_policy_page_url_mobile = u'http://example.com/privacy/mobile'
    legal_notice_page_url = u'http://example.com/legal/'
    legal_notice_page_url_mobile = u'http:/example.com/legal/mobile'
    orderreview_page_url = u'http://example.com/orderreview'
    lots_orderreview_page_url = u'http://example.com/lots/review'
    extra_footer_links = [u'aaa', u'http://example.com/aaa']
    extra_footer_links_mobile = [u'aaa', u'http://example.com/aaa']
    mail_filter_domain_notice_template = u'XXXX'
    extra_form_fields = []
    header_image_url = u'http://example.com/'
    header_image_url_mobile = u'http://example.com/'
    booster_or_fc_cart = False
    booster_cart = False
    fc_cart = False
    embedded_html_complete_page = u''
    embedded_html_complete_page_mobile = u''
    embedded_html_complete_page_smartphone = u''


@implementer(ICartResource)
class DummyCartResource(object):
    def __init__(self, request):
        self.request = request
        self.performance = DummyPerformance()
        self.cart_setting = DummyCartSetting()

    @reify
    def cart(self):
        return _dummy_cart(self.performance)

    @property
    def read_only_cart(self):
        return self.cart

    host_base_url = '/'


def index_view(context, request):
    from altair.app.ticketing.core.models import Organization, Host
    links = [("dummy.cart.payment", u"支払方法選択画面"),
             ("dummy.payment.confirm", u"注文確認画面"),
             ("dummy.payment.complete", u"注文完了画面"),
             ("dummy.timeout", u"タイムアウト画面"),
             ("dummy.notfound", u"404画面")]
    template = Template(u"""
%for organization in organizations:
<h3>${organization.name}</h3>
<ul>
%for route_name, description in links:
  <li><a href="${request.route_path(route_name, _query=dict(organization_id=organization.id))}">${description}</a></li>
%endfor
</ul>
%endfor
""")
    organizations = Organization \
        .query \
        .filter_by(deleted_at=None) \
        .filter(Host.organization_id == Organization.id) \
        .all()
    return Response(template.render(request=request, links=links, organizations=organizations))


def _get_mailmagazines_from_organization(organization):
    return mailmag_models.MailMagazine.query.outerjoin(mailmag_models.MailSubscription) \
        .filter(mailmag_models.MailMagazine.organization == organization)


def confirm_view(context, request):
    """dummy用購入確認ページのview
    """
    from collections import defaultdict
    from .api import get_organization
    form = mock.Mock()
    cart = context.cart
    request.session["order"] = defaultdict(str)
    magazines = _get_mailmagazines_from_organization(get_organization(request))
    user = mock.Mock()
    return dict(cart=cart, mailmagazines=magazines, user=user, form=form)


def complete_view(context, request):
    """dummy用購入完了ページのview
    """
    order = DummyOrder(context.performance)
    return dict(order=order)


def payment_view(context, request):
    """dummy用決済/引取方法と配送情報入力ページのview
    """
    from .schemas import ClientForm
    request.session.flash(u"お支払い方法／受け取り方法をどれかひとつお選びください")
    context.cart_setting = mock.Mock()
    params = dict(
        form=ClientForm(context=mock.Mock()),
        payment_delivery_methods=[],
        user=mock.Mock(),
        user_profile=mock.Mock(),
        )
    return params


def timeout_view(context, request):
    """dummy用session timeoutページのview
    """
    return {}


def notfound_view(context, request):
    """dummy用404ページのview
    """
    return {}
