# encoding: utf-8

import logging
from datetime import datetime
from decimal import Decimal
from zope.interface import implementer, directlyProvides
from altair.app.ticketing.core.models import PaymentMethod, DeliveryMethod
from .interfaces import (
    IFakeObjectFactory,
    IPurchaseInfoMail,
    IPointGrantHistoryEntryInfoMail,
    ILotEntryInfoMail,
    )

logger = logging.getLogger(__name__)

class FakeObject(unicode):
    @classmethod
    def create(cls, name="*", **kwargs):
        o = cls(name)
        for k, v in kwargs.iteritems():
            o.__dict__[k] = v
        return o

    def __init__(self, name="*"):
        self.name = name
        self.items = {}
        self._fake_root = None

    def __repr__(self):
        return "%r %s" % (self.__class__, self.name)

    def __create_child__(self, name):
        longname = "%s.%s" % (self.name , name)
        child = self.__class__(longname)
        child._fake_root = self._fake_root
        return child

    def __getattr__(self, name):
        child = self.__create_child__(name) ## object
        setattr(self, name, child)
        return child

    def __getitem__(self, name):
        v = self.items.get(name)
        if v is None:
            v = self.items[name] = self.__create_child__(name) ## Dict
        return v

    def __iter__(self):
        return iter([self.__class__()])

    def __str__(self):
        return self.name

    def __add__(self, n):
        return int(self)+n

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __call__(self, *args, **kwargs):
        logger.debug("warn call() return self")
        return self

    def __nonzero__(self):
        return False


def create_shipping_address(request, args):
    shipping_address = FakeObject("ShippingAddress")
    shipping_address.first_name = u"名"
    shipping_address.last_name = u"姓"
    shipping_address.first_name_kana = u"メイ"
    shipping_address.last_name_kana = u"セイ"
    shipping_address.email_1 = "****@example.com"
    return shipping_address

def create_fake_order(request, args):
    organization = args.get('organization')
    payment_method_id = args.get('payment_method_id')
    delivery_method_id = args.get('delivery_method_id')
    event = args.get('event')
    performance = args.get('performance')
    now = args.get('now') or datetime.now()

    order = FakeObject("T")
    order.ordered_from = organization
    order.order_no = None
    order.created_at = now
    order._cached_mail_traverser = None

    if event:
        order.performance._fake_root = event
    else:
        order.performance._fake_root = organization

    order.payment_delivery_pair.payment_method.payment_plugin_id = 1 #dummy
    payment_method = PaymentMethod.query.filter_by(id=payment_method_id).first()
    if payment_method:
        order.payment_delivery_pair.payment_method = payment_method

    order.payment_delivery_pair.delivery_method.delivery_plugin_id = 1 #dummy
    delivery_method = DeliveryMethod.query.filter_by(id=delivery_method_id).first()
    if delivery_method:
        order.payment_delivery_pair.delivery_method = delivery_method

    order.performance.start_on = datetime.now()

    if event:
        order.performance.event = event
    if performance:
        order.performance = performance
    return order

@implementer(IFakeObjectFactory)
class FakeOrderFactory(object):
    def __init__(self, impl):
        pass

    def __call__(self, request, args):
        return create_fake_order(request, args)

@implementer(IFakeObjectFactory)
class FakeLotEntryElectedWishPairFactory(object):
    def __init__(self, impl):
        pass

    def create_fake_lot_entry(self, request, args):
        organization = args.get('organization')
        payment_method_id = args.get('payment_method_id')
        delivery_method_id = args.get('delivery_method_id')
        event = args.get('event')
        performance = args.get('performance')
        now = args.get('now') or datetime.now()

        lot_entry = FakeObject("T")
        lot_entry.entry_no = lot_entry.order_no = None
        lot_entry.lot_entryed_from = organization
        lot_entry.created_at = now
        lot_entry._cached_mail_traverser = None

        if performance:
            pass
        elif event:
            pass
        else:
            lot_entry.lot.event._fake_root = organization #lot_entry


        lot_entry.payment_delivery_method_pair.payment_method.payment_plugin_id = 1 #dummy
        payment_method = PaymentMethod.query.filter_by(id=payment_method_id).first()
        if payment_method:
            lot_entry.payment_delivery_method_pair.payment_method = payment_method

        lot_entry.payment_delivery_method_pair.delivery_method.delivery_plugin_id = 1 #dummy
        delivery_method = DeliveryMethod.query.filter_by(id=delivery_method_id).first()
        if delivery_method:
            lot_entry.payment_delivery_method_pair.delivery_method = delivery_method

        if event:
            lot_entry.lot.event = event #lot_entry
        if performance:
            lot_entry.lot.event = performance.event #lot_entry
        return lot_entry

    def create_fake_elected_wish(self, request, args):
        performance = args.get('performance')

        elected_wish = FakeObject("ElectedWish")
        if performance:
            elected_wish.performance = performance
        return elected_wish

    def __call__(self, request, args):
        return (
            self.create_fake_lot_entry(request, args),
            self.create_fake_elected_wish(request, args),
            )

@implementer(IFakeObjectFactory)
class FakePointGrantHistoryEntryFactory(object):
    def __init__(self, impl):
        pass

    def __call__(self, request, args):
        from altair.app.ticketing.loyalty.models import PointGrantStatusEnum
        point_grant_history_entry = FakeObject("PointGrantHistoryEntry")
        point_grant_history_entry._cached_mail_traverser = None
        point_grant_history_entry.grant_status = PointGrantStatusEnum.InvalidPointAccountNumber.v
        point_grant_history_entry.amount = Decimal('123.00')
        point_grant_history_entry.submitted_on = datetime.now()
        point_grant_history_entry.order = create_fake_order(request, args)
        point_grant_history_entry.order.shipping_address = create_shipping_address(request, args)
        return point_grant_history_entry

def includeme(config):
    config.registry.registerAdapter(FakeOrderFactory, [IPurchaseInfoMail], IFakeObjectFactory)
    config.registry.registerAdapter(FakeLotEntryElectedWishPairFactory, [ILotEntryInfoMail], IFakeObjectFactory)
    config.registry.registerAdapter(FakePointGrantHistoryEntryFactory, [IPointGrantHistoryEntryInfoMail], IFakeObjectFactory)
