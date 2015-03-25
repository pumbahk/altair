# -*- coding:utf-8 -*-

import logging
import urlparse
from lxml import etree
from base64 import b64encode
from datetime import datetime
import warnings
from collections import OrderedDict
from zope.interface import implementer
from sqlalchemy.orm.exc import NoResultFound
from altair.app.ticketing.core.models import ChannelEnum
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.cart.models import Cart
from altair.app.ticketing.orders.models import Order
from altair.sqla import session_scope
from . import interfaces
from . import models as m
from .payload import (
    RESULT_FLG_SUCCESS,
    RESULT_FLG_FAILED,
    )
from .payload import AnshinCheckoutPayloadBuilder, AnshinCheckoutHTMLFormBuilder
from .interfaces import IAnshinCheckoutCommunicator, IAnshinCheckoutPayloadResponseFactory
from .exceptions import AnshinCheckoutAPIError

logger = logging.getLogger(__name__)

def _get_setting(settings, current_name, deprecated_name):
    v = settings.get(current_name)
    if v is None:
        logger.warning("%s is not given. using deprecated %s instead" % (current_name, deprecated_name))
        v = settings.get(deprecated_name)
    return v

def get_checkout_service(request, organization_or_organization_id=None, channel=None):
    settings = request.registry.settings

    success_url = _get_setting(settings, 'altair.anshin_checkout.success_url', 'altair_checkout.success_url')
    fail_url = _get_setting(settings, 'altair.anshin_checkout.fail_url', 'altair_checkout.fail_url')

    success_url = urlparse.urljoin(request.application_url, success_url)
    fail_url = urlparse.urljoin(request.application_url, fail_url)

    nonmobile_checkin_url = _get_setting(settings, 'altair.anshin_checkout.checkin_url', 'altair_checkout.checkin_url')
    mobile_checkin_url = _get_setting(settings, 'altair.anshin_checkout.mobile_checkin_url', 'altair_checkout.mobile_checkin_url')

    params = dict(
        success_url=success_url,
        fail_url=fail_url,
        nonmobile_checkin_url=nonmobile_checkin_url,
        mobile_checkin_url=mobile_checkin_url,
        is_test=_get_setting(settings, 'altair.anshin_checkout.test_mode', 'altair_checkout.is_test') or u'0',
        service_id=None,
        auth_method=None,
        secret=None
    )

    if organization_or_organization_id and channel:
        from altair.app.ticketing.core.models import Organization
        if isinstance(organization_or_organization_id, Organization):
            organization_id = organization_or_organization_id.id
            warnings.warn("organization_id should be passed to get_checkout_service() instead of an organization object", DeprecationWarning)
        else:
            organization_id = organization_or_organization_id
        shop_settings = m._session.query(m.RakutenCheckoutSetting).filter_by(
            organization_id=organization_id,
            channel=channel.v
        ).first()
        if not shop_settings:
            raise Exception('RakutenCheckoutSetting not found (organization_id=%s, channel=%s)' % (organization_id, channel.v))

        params.update(dict(
            service_id=shop_settings.service_id,
            auth_method=shop_settings.auth_method,
            secret=shop_settings.secret
        ))

    pb = AnshinCheckoutPayloadBuilder(
        service_id=params['service_id'],
        success_url=params['success_url'],
        fail_url=params['fail_url'],
        auth_method=params['auth_method'],
        secret=params['secret'],
        is_test=params['is_test']
        )
    hfb = AnshinCheckoutHTMLFormBuilder(
        payload_builder=pb,
        channel=channel,
        nonmobile_checkin_url=params['nonmobile_checkin_url'],
        mobile_checkin_url=params['mobile_checkin_url'],
        )

    comm = get_communicator(request)
    now = datetime.now()
    return AnshinCheckoutAPI(
        request=request,
        session=m._session,
        now=now,
        payload_builder=pb,
        html_form_builder=hfb,
        communicator=comm
        )

def get_communicator(request_or_registry):
    if hasattr(request_or_registry, 'registry'):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IAnshinCheckoutCommunicator)

def anshin_checkout_session(func):
    from .models import _session
    return session_scope('anshin_checkout', _session)(func)

def remove_default_session():
    m._session.remove()

BASIC_FEE_ITEMS = [
    ('delivery_fee', 'refund_delivery_fee', u'引取手数料'),
    ('system_fee', 'refund_system_fee', u'システム利用料'),
    ]

def get_fee_items_dict(request, order_like):
    retval = OrderedDict(
        (triplet[0], triplet)
        for triplet in BASIC_FEE_ITEMS
        )
    if order_like.special_fee:
        retval['special_fee'] = ('special_fee', 'refund_special_fee', order_like.special_fee_name)
    return retval

def build_checkout_object_from_order_like(request, order_like):
    checkout_object = m.Checkout(
        orderCartId=order_like.order_no,
        orderTotalFee=int(order_like.total_amount)
        )
    for item in order_like.items:
        checkout_object.items.append(
            m.CheckoutItem(
                itemId=unicode(item.product.id),
                itemName=item.product.name,
                itemNumbers=item.quantity,
                itemFee=int(item.price)
                )
            )
    # 手数料も商品として登録する
    for item_id, (attr_name, _, name) in get_fee_items_dict(request, order_like).items():
        fee = getattr(order_like, attr_name)
        if fee is not None:
            fee = int(fee)
            if fee > 0:
                checkout_object.items.append(
                    m.CheckoutItem(
                        itemId=item_id,
                        itemName=name,
                        itemNumbers=1,
                        itemFee=fee
                        )
                    )
    return checkout_object

def get_cart_id_by_order_no(request, order_no):
    from altair.app.ticketing.models import DBSession as session
    from altair.app.ticketing.cart.models import Cart
    return session.query(Cart).filter_by(order_no=order_no).one().id

def get_checkout_object(request, session, order_no):
    expr = (m.Checkout.orderCartId == order_no)
    return session.query(m.Checkout).filter(expr).one()

def get_checkout_object_by_order_cart_id(request, session, orderCartId):
    return get_checkout_object(request, session, orderCartId)

def get_checkout_object_by_id(request, session, id):
    return session.query(m.Checkout) \
        .filter(m.Checkout.id == id) \
        .one()

def update_checkout_object_by_order_like(request, session, checkout_object, order_like, refund_record=None):
    total_amount = order_like.total_amount
    if refund_record is not None and \
       refund_record.refund_total_amount is not None:
        total_amount -= refund_record.refund_total_amount
    fee_items_dict = get_fee_items_dict(request, order_like)
    checkout_object.orderTotalFee = total_amount
    checkout_object_item_map = dict(
        (item.itemId, item)
        for item in checkout_object.items
        if item.itemId not in fee_items_dict
        )
    checkout_object_fee_item_map = dict(
        (item.itemId, item)
        for item in checkout_object.items
        if item.itemId in fee_items_dict
        )
    order_like_item_map = dict(
        (unicode(item.product.id), item)
        for item in order_like.items
        )

    added_checkout_items = {}
    updated_checkout_items = {}
    deleted_checkout_items = {}

    for k, item in order_like_item_map.items():
        checkout_item = checkout_object_item_map.get(k)
        price = item.price
        if refund_record is not None:
            item_refund_record = refund_record.get_item_refund_record(item)
            if item_refund_record is not None and \
               item_refund_record.refund_price is not None:
                price -= item_refund_record.refund_price
        if checkout_item is None:
            added_checkout_items[item.product.id] = \
                m.CheckoutItem(
                    itemId=unicode(item.product.id),
                    itemName=item.product.name,
                    itemNumbers=item.quantity,
                    itemFee=int(price)
                    )
        else:
            checkout_item.itemName = item.product.name
            checkout_item.itemNumbers = item.quantity
            checkout_item.itemFee = int(price)
            updated_checkout_items[checkout_item.itemId] = checkout_item
    for k, checkout_item in checkout_object_item_map.items():
        if k not in order_like_item_map:
            deleted_checkout_items[k] = checkout_item

    for k, (attr_name, refund_attr_name, item_name) in fee_items_dict.items():
        checkout_item = checkout_object_fee_item_map.get(k)
        fee = getattr(order_like, attr_name, None)
        if fee is not None:
            if refund_record is not None:
                fee -= getattr(refund_record, refund_attr_name)
            fee = int(fee)
        if checkout_item is None:
            if fee > 0:
                added_checkout_items[k] = m.CheckoutItem(
                    itemId=k,
                    itemName=item_name,
                    itemNumbers=1,
                    itemFee=fee
                    )
        else:
            checkout_item.itemName = item_name
            checkout_item.itemNumbers = 1
            checkout_item.itemFee = fee
            updated_checkout_items[checkout_item.itemId] = checkout_item

    for k, checkout_item in checkout_object_fee_item_map.items():
        if k not in fee_items_dict:
            deleted_checkout_items[k] = checkout_item

    logger.info("added items: %d" % len(added_checkout_items))
    logger.info("deleted items: %d" % len(deleted_checkout_items))
    logger.info("updated items: %d" % len(updated_checkout_items))

    for i in range(len(checkout_object.items) - 1, -1, -1):
        checkout_item = checkout_object.items[i]
        updated_checkout_item = updated_checkout_items.get(checkout_item.itemId)
        if checkout_item.itemId in deleted_checkout_items:
            del checkout_object.items[i]
        elif updated_checkout_item is not None:
            checkout_object.items[i] = updated_checkout_item

    for checkout_item in added_checkout_items.values():
        checkout_object.items.append(checkout_item)

    return checkout_object

@implementer(IAnshinCheckoutPayloadResponseFactory)
class AnshinCheckoutAPI(object):
    def __init__(self, request, session, now, payload_builder, html_form_builder, communicator):
        self.request = request
        self.session = session
        self.now = now
        self.pb = payload_builder
        self.hfb = html_form_builder
        self.comm = communicator

    def create_checkout_object(self, orderCartId):
        """IAnshinCheckoutPayloadResponseFactory"""
        if orderCartId is None:
            return m.Checkout(orderCartId=orderCartId)
        else:
            return get_checkout_object_by_order_cart_id(self.request, self.session, orderCartId)

    def create_checkout_item_object(self):
        """IAnshinCheckoutPayloadResponseFactory"""
        return m.CheckoutItem()

    def get_or_create_checkout_object(self, order_like):
        """外部でロックをかけていることが前提 (Cart の for update などで) なので注意!"""
        try:
            retval = get_checkout_object(self.request, self.session, order_like.order_no)
        except NoResultFound:
            retval = build_checkout_object_from_order_like(self.request, order_like)
        return retval

    def get_order_settled_at(self, order_like):
        return self.get_checkout_object_by_order_no(order_like.order_no).sales_at

    def get_order_authorized_at(self, order_like):
        return self.get_checkout_object_by_order_no(order_like.order_no).authorized_at

    def get_checkout_object_by_order_no(self, order_no):
        try:
            return get_checkout_object(self.request, self.session, order_no)
        except NoResultFound:
            return None

    def get_checkout_object_by_id(self, id):
        try:
            return get_checkout_object_by_id(self.request, self.session, id)
        except NoResultFound:
            return None

    def mark_authorized(self, order_no):
        checkout_object = self.get_checkout_object_by_order_no(order_no)
        checkout_object.authorized_at = self.now
        self.session.add(checkout_object)
        self.session.commit()

    def request_fixation_order(self, order_like_list):
        checkout_object_list = [get_checkout_object(self.request, self.session, order_like.order_no) for order_like in order_like_list]
        xml = self.pb.create_order_control_request_xml(checkout_object_list)
        try:
            res = self.comm.send_order_fixation_request(xml)
            result = self.pb.parse_order_control_response_xml(res)
            if 'statusCode' in result and result['statusCode'] != '0':
                error_code = result['apiErrorCode'] if 'apiErrorCode' in result else ''
                raise AnshinCheckoutAPIError(
                    u'楽天ID決済の決済確定に失敗しました',
                    error_code
                    )
            for checkout in checkout_object_list:
                checkout.sales_at = self.now
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return result

    def request_cancel_order(self, order_like_list):
        checkout_object_list = [get_checkout_object(self.request, self.session, order_like.order_no) for order_like in order_like_list]
        xml = self.pb.create_order_control_request_xml(checkout_object_list)
        try:
            res = self.comm.send_order_cancel_request(xml)
            result = self.pb.parse_order_control_response_xml(res)
            if 'statusCode' in result and result['statusCode'] != '0':
                error_code = result['apiErrorCode'] if 'apiErrorCode' in result else ''
                raise AnshinCheckoutAPIError(
                    u'楽天ID決済のキャンセルに失敗しました',
                    error_code
                    )
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return result

    def request_change_order(self, order_like_refund_record_pairs):
        checkout_object_list = [
            update_checkout_object_by_order_like(
                self.request, self.session,
                get_checkout_object(self.request, self.session, order_like.order_no),
                order_like,
                refund_record
                )
            for order_like, refund_record in order_like_refund_record_pairs
            ]
        xml = self.pb.create_order_control_request_xml(checkout_object_list, with_items=True)
        try:
            res = self.comm.send_order_change_request(xml)
            result = self.pb.parse_order_control_response_xml(res)
            if 'statusCode' in result and result['statusCode'] != '0':
                error_code = result['apiErrorCode'] if 'apiErrorCode' in result else ''
                raise AnshinCheckoutAPIError(
                    u'楽天ID決済の金額変更に失敗しました',
                    error_code
                    )
            self.session.commit()
        except:
            self.session.rollback()
            raise
        return result

    def save_order_complete(self, params):
        confirmId = params['confirmId']
        xml = confirmId.replace(' ', '+').decode('base64')
        checkout_object = self.pb.parse_order_complete_xml(self, etree.fromstring(xml))
        self.session.add(checkout_object)
        self.session.commit()
        return checkout_object

    def create_order_complete_response_xml(self, result, complete_time):
        return etree.tostring(self.pb.create_order_complete_response_xml(result, complete_time), xml_declaration=True, encoding='utf-8')

    def build_checkout_request_form(self, order_like, success_url=None, fail_url=None):
        """この関数の呼び出しは同期していないといけない (同時に違うリクエストが呼び出す状況を作ってはいけない)"""
        # checkoutをXMLに変換
        checkout_object = self.get_or_create_checkout_object(order_like)
        self.session.add(checkout_object)
        self.session.commit()

        return checkout_object, self.hfb.build_checkout_request_form(
            checkout_object,
            success_url=success_url,
            fail_url=fail_url
            )
