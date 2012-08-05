# -*- coding:utf-8 -*-
from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound
from datetime import datetime, timedelta
from sqlalchemy.orm.exc import NoResultFound

from ..interfaces import IPaymentPlugin, ICartPayment, IOrderPayment
from ..interfaces import IDeliveryPlugin, ICartDelivery, IOrderDelivery
from ..interfaces import IPaymentDeliveryPlugin
from .models import DBSession
from ticketing.core import models as c_models
from .. import logger
from .. import helpers as h
from .. import api as a

from ticketing.cart.rakuten_auth.api import authenticated_user
from ticketing.sej.ticket import SejTicketDataXml
from ticketing.sej.models import SejOrder
from ticketing.sej.payment import request_order
from ticketing.sej.resources import SejPaymentType, SejTicketType
from ticketing.sej.utils import han2zen

PAYMENT_PLUGIN_ID = 3
DELIVERY_PLUGIN_ID = 2

def includeme(config):
    # 決済系(マルチ決済)
    config.add_payment_plugin(SejPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_delivery_plugin(SejDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.add_payment_delivery_plugin(SejPaymentDeliveryPlugin(), PAYMENT_PLUGIN_ID, DELIVERY_PLUGIN_ID)
    config.scan(__name__)

def get_payment_due_at(current_date, cart):
    if cart.payment_delivery_pair.payment_period_days:
        payment_due_at = current_date + timedelta(days=cart.payment_delivery_pair.payment_period_days)
    else:
        payment_due_at = current_date + timedelta(days=3)
    return payment_due_at

def get_ticketing_start_at(current_date, cart):
    if cart.payment_delivery_pair.issuing_start_at:
        ticketing_start_at = cart.payment_delivery_pair.issuing_start_at
    else:
        ticketing_start_at = current_date + timedelta(days=cart.payment_delivery_pair.issuing_interval_days)
    return ticketing_start_at

def get_sej_order(order):
    try:
        sej_order = SejOrder.filter(SejOrder.order_id == order.order_no).one()
    except NoResultFound, e:
        return None
    return sej_order

def get_ticket(order_no, product_item):
    performance = product_item.performance
    xml = u"""<?xml version="1.0" encoding="UTF-8" ?>
<TICKET>
<b><![CDATA[:mm U :#000 rg
1e-3 S 134333 2288m134106 2076 133798 1827 133430 1674c133430 3002l133067 3002l133067 567l133436 631l133445 635 133509 644 133509 681c133509 699 133430 748 133430 764c133430 1572l133574 1345l133731 1412 133832 1452 134096 1624c134340 1784 134453 1886 134576 1993c134333 2288l h130856 1803m130804 1618 130733 1461 130638 1305c130911 1200l131025 1382 131087 1572 131121 1698c130856 1803l h131889 1403m131861 1418 131858 1430 131827 1551c131597 2494 130976 2854 130681 3026c130435 2808l131031 2513 131450 2092 131566 1222c131867 1314l131907 1326 131929 1348 131929 1369c131929 1388 131923 1391 131889 1403c130290 1953m130238 1778 130158 1615 130057 1458c130340 1351l130444 1514 130524 1674 130576 1846c130290 1953l h128697 1437m128691 1631 128688 1935 128507 2322c128289 2793 127963 3048 127793 3183c127419 2952l127576 2857 127917 2648 128138 2208c128304 1876 128313 1603 128316 1437c127671 1437l127450 1781 127326 1917 127185 2064c126826 1864l127281 1443 127539 1025 127729 395c128079 521l128098 527 128156 549 128156 582c128156 604 128147 610 128116 619c128086 634 128083 638 128067 678c128018 798 127981 884 127877 1090c129457 1090l129457 1437l128697 1437l h125208 1858m125085 2467 124833 2756 124313 3094c124015 2832l124513 2549 124732 2316 124833 1858c123738 1858l123738 1517l124870 1517l124873 1486 124876 1428 124876 1326c124876 1219 124873 1151 124858 1080c124574 1145 124409 1172 124138 1197c123972 890l124200 877 124848 834 125503 499c125755 733l125764 742 125792 773 125792 795c125792 807 125786 813 125777 816c125678 816l125660 816 125657 819 125632 828c125530 874 125454 911 125242 979c125245 1090 125254 1262 125251 1369c125251 1449 125248 1465 125248 1517c126068 1517l126068 1858l125208 1858l h115365 493m115365 112l114663 494l114663 874l115365 493l h113328 1188m114114 1188l114114 1516l113328 1516l113328 1188l h113328 584m114114 584l114114 872l113328 872l113328 584l h115365 1970m115365 1598l114663 1216l114663 1597l115351 1970l113894 1970l113894 1839l114465 1839l114465 265l113857 265l113937 0l113563 0l113482 265l112980 265l112980 1839l113542 1839l113542 1970l112096 1970l112782 1598l112782 1217l112082 1598l112082 2311l113256 2311l113008 2549 112621 2829 112054 3026c112000 3045l112000 3403l112108 3365l112723 3143 113204 2857 113542 2513c113542 3454l113894 3454l113894 2513l114236 2863 114720 3147 115335 3358c115442 3395l115442 3037l115387 3019l114818 2830 114430 2550 114179 2311c115365 2311l115365 1970l115365 1970l h112082 112m112082 493l112782 873l112782 493l112082 112l h122441 476m122441 128l118999 128l118999 476l120498 476l120498 987l120498 1121 120495 1192 120489 1288c119106 1288l119106 1640l120436 1640l120337 2041 120026 2672 119046 3019c118992 3039l118992 3447l119102 3405l120138 3008 120526 2560 120711 1991c120935 2570 121467 3035 122328 3405c122441 3454l122441 3032l122386 3014l121574 2749 121091 2137 120959 1640c122323 1640l122323 1288l120881 1288l120871 1218 120864 1134 120864 987c120864 476l122441 476l117028 1173m117263 1173l117408 1173 117526 1293 117526 1439c117526 1584 117408 1703 117263 1703c117028 1703l117028 1173l117563 1960m117748 1856 117866 1656 117866 1439c117866 1105 117596 833 117263 833c116688 833l116688 2621l117028 2621l117028 2043l117203 2043l117217 2063 117619 2621 117619 2621c118037 2621l118037 2621 117593 2002 117563 1960c118902 1727m118902 2647 118156 3393 117236 3393c116316 3393 115570 2647 115570 1727c115570 807 116316 61 117236 61c118156 61 118902 807 118902 1727c f
:f15 hc 1 S :b hc
12 fs 14 0 m 93 12 "BLUE MAN GROUP IN " X 10 fs
14 8 m 93 5 "%(event_name)s " X
14 13 m 93 9 "2012年 08月 31日(金)<br /> 12:30 開場 13:00 開演" X
65 13 m 93 9 "ポンチョ席 1列%(seat_number)s番<br/>\\\\%(ticket_price)s (税込)" X
7 fs
14 22 m 90 10 "主催: ブルーマングループ IN 、LLP<br/>お問合せ: ブルーマングループ公演事務局 03-5414-3255<br/>後援: 東京都、米国大使館、港区、東京メトロ<br/>営利目的の転売禁止<br/>4歳以下入場不可<br/>※車イスでご来場のお客様は、事前に六本木ブルーシアター（03-5770－7064）までお問い合わせください。" X
6.35 fs
13.3 42.4 m 30 2 "予約番号：" X 25.1 42.4 m 30 2 "%(order_id)s" X
13.3 44.8 m 80 2 "お問合せ先：楽天チケット お問い合わせセンター 03-9876-5432" X
8 fs
:b hc 112 5 m 28 8 "BLUE MAN GROUP IN " X
112 14 m 28 12 "開催日 2012年<br/>8月31日(金)<br/>開場 12:30<br/>開演 13:00<br/>" X
112 32 m 28 15 "ポンチョ席<br/>1列%(seat_number)s番<br/>\\\\%(ticket_price)s(税込)" X
:b hc 7 fs 112 50 m 28 4 "%(order_id)s" X
pc
]]></b>
<FIXTAG01></FIXTAG01>
<FIXTAG02></FIXTAG02>
<FIXTAG03></FIXTAG03>
<FIXTAG04></FIXTAG04>
<FIXTAG05></FIXTAG05>
<FIXTAG06></FIXTAG06>
</TICKET>""" % dict(
        event_name          = performance.event.title,
        performance_name    = performance.name,
        ticket_price        = product_item.price,
        seat_number         = '11',
        order_id            = order_no
    )

    return dict(
        ticket_type         = SejTicketType.TicketWithBarcode,
        event_name          = han2zen(performance.event.title)[:40].replace(' ', ''),
        performance_name    = han2zen(performance.name)[:40].replace(' ', ''),
        ticket_template_id  = u'TTTS000001',
        performance_datetime= performance.start_on,
        xml = SejTicketDataXml(xml)
    )

def get_tickets(order):

    tickets = list()
    for ordered_product in order.items:
        for item in ordered_product.ordered_product_items:
            ticket = get_ticket(order.order_no, item.product_item)
            tickets.append(ticket)
    return tickets

def get_tickets_from_cart(cart):
    tickets = list()
    for product in cart.products:
        for item in product.items:
            ticket = get_ticket(u'%012d' % cart.id, item.product_item)
            tickets.append(ticket)
    return tickets

@implementer(IPaymentPlugin)
class SejPaymentPlugin(object):

    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        """ 売り上げ確定 """
        logger.debug('Sej Payment')
        order = c_models.Order.create_from_cart(cart)
        cart.finish()

        shipping_address = order.shipping_address
        performance = order.performance
        current_date = datetime.now()

        payment_due_at = get_payment_due_at(current_date,order)
        ticketing_start_at = get_ticketing_start_at(current_date,order)
        ticketing_due_at = order.payment_delivery_pair.issuing_end_at
        tel1 = shipping_address.tel_1.replace('-', '')
        tel2 = shipping_address.tel_2.replace('-', '')
        sej_order = get_sej_order(order)


        from pyramid.threadlocal import get_current_registry
        settings = get_current_registry().settings
        api_key = settings['sej.api_key']
        api_url = settings['sej.inticket_api_url']

        if not sej_order:
            request_order(
                shop_name           = performance.event.organization.name,
                shop_id             = u'30520',
                contact_01          = u'022-215-8138',
                contact_02          = u'仙台89ERS　ブースター事務局　TEL: 022-215-8138　(平日：9:00〜18:00)',
                order_id            = order.order_no,
                username            = u'%s%s' % (shipping_address.last_name, shipping_address.first_name),
                username_kana       = u'%s%s' % (shipping_address.last_name_kana, shipping_address.first_name_kana),
                tel                 = tel1 if tel1 else tel2,
                zip                 = shipping_address.zip.replace('-', ''),
                email               = shipping_address.email,
                total               = order.total_amount,
                ticket_total        = cart.tickets_amount,
                commission_fee      = order.system_fee + order.transaction_fee,
                payment_type        = SejPaymentType.PrepaymentOnly,
                ticketing_fee       = order.delivery_fee,
                payment_due_at      = payment_due_at,
                ticketing_start_at  = ticketing_start_at,
                ticketing_due_at    = ticketing_due_at,
                regrant_number_due_at = performance.start_on + timedelta(days=1) if performance.start_on else
                current_date + timedelta(days=365),
                secret_key = api_key,
                hostname = api_url
            )

        return order


@implementer(IDeliveryPlugin)
class SejDeliveryPlugin(object):
    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        logger.debug('Sej Delivery')

        order_no = str(cart.id)
        shipping_address = cart.shipping_address
        performance = cart.performance
        current_date = datetime.now()

        payment_due_at = get_payment_due_at(current_date,cart)
        ticketing_start_at = get_ticketing_start_at(current_date,cart)
        ticketing_due_at = cart.payment_delivery_pair.issuing_end_at
        tickets = get_tickets_from_cart(cart)
        order_no = cart.order_no
        tel1 = shipping_address.tel_1.replace('-', '')
        tel2 = shipping_address.tel_2.replace('-', '')

        try:
            sej_order = SejOrder.filter(SejOrder.order_id == order_no).one()
        except NoResultFound, e:
            sej_order = None

        if not sej_order:
            request_order(
                shop_name           = performance.event.organization.name,
                shop_id             = u'30520',
                contact_01          = u'00-0000-0000',
                contact_02          = u'楽天チケット お問い合わせセンター 050-5830-6860',
                order_id            = order_no,
                username            = u'%s%s' % (shipping_address.last_name, shipping_address.first_name),
                username_kana       = u'%s%s' % (shipping_address.last_name_kana, shipping_address.first_name_kana),
                tel                 = tel1 if tel1 else tel2,
                zip                 = shipping_address.zip.replace('-', ''),
                email               = shipping_address.email,
                total               = 0,
                ticket_total        = 0,
                commission_fee      = 0,
                payment_type        = SejPaymentType.Paid,
                ticketing_fee       = 0,
                payment_due_at      = payment_due_at,
                ticketing_start_at  = ticketing_start_at,
                ticketing_due_at    = ticketing_due_at,
                regrant_number_due_at = performance.start_on + timedelta(days=1),
                tickets=tickets
            )

@implementer(IDeliveryPlugin)
class SejPaymentDeliveryPlugin(object):
    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        """  """
        logger.debug('Sej Payment and Delivery')
        order = c_models.Order.create_from_cart(cart)
        cart.finish()

        sej_order = get_sej_order(order)
        if not sej_order:
            shipping_address = cart.shipping_address
            performance = cart.performance
            current_date = datetime.now()
            payment_due_at = get_payment_due_at(current_date,order)
            ticketing_start_at = get_ticketing_start_at(current_date,order)
            ticketing_due_at = cart.payment_delivery_pair.issuing_end_at
            tel1 = shipping_address.tel_1.replace('-', '')
            tel2 = shipping_address.tel_2.replace('-', '')
            tickets = get_tickets(order)
            request_order(
                shop_name           = performance.event.organization.name,
                shop_id             = u'30520',
                contact_01          = u'00-0000-0000',
                contact_02          = u'楽天チケット お問い合わせセンター 050-5830-6860',
                order_id            = order.order_no,
                username            = u'%s%s' % (shipping_address.last_name, shipping_address.first_name),
                username_kana       = u'%s%s' % (shipping_address.last_name_kana, shipping_address.first_name_kana),
                tel                 = tel1 if tel1 else tel2,
                zip                 = shipping_address.zip.replace('-', ''),
                email               = shipping_address.email,
                total               = order.total_amount,
                ticket_total        = cart.tickets_amount,
                commission_fee      = order.system_fee + order.transaction_fee,
                payment_type        = SejPaymentType.Prepayment if  jPaymentType.CashOnDelivery,
                ticketing_fee       = order.delivery_fee,
                payment_due_at      = payment_due_at,
                ticketing_start_at  = ticketing_start_at,
                ticketing_due_at    = ticketing_due_at,
                regrant_number_due_at = performance.start_on + timedelta(days=1),
                tickets=tickets
            )

        return order


@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/carts/sej_delivery_complete.html')
def sej_delivery_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order)
    return dict(
        order=order,
        sej_order=sej_order
    )

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/carts/sej_delivery_confirm.html')
def sej_delivery_confirm_viewlet(context, request):
    return Response(text=u'セブンイレブン受け取り')

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/sej_payment_complete.html')
def sej_payment_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order)
    return dict(
        order=order,
        sej_order=sej_order
    )

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/carts/sej_payment_confirm.html')
def sej_payment_confirm_viewlet(context, request):
    return Response(text=u'セブンイレブン支払い')
