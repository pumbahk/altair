# -*- coding:utf-8 -*-

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.core.models import Event, Product
from altair.app.ticketing.lots.models import Lot, LotEntry
from altair.app.ticketing.carturl.api import (
    get_lots_cart_url_builder,
    get_agreement_lots_cart_url_builder,
    get_cart_now_url_builder
)

from altair.app.ticketing.events.lots.models import LotEntryReportSetting
from altair.app.ticketing.resources import TicketingAdminResource

class LotResourceBase(TicketingAdminResource):
    @property
    def event(self):
        raise NotImplementedError

class LotCollectionResource(LotResourceBase):
    def __init__(self, request):
        super(LotCollectionResource, self).__init__(request)
        try:
            self.event_id = long(self.request.matchdict.get('event_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound

    @reify
    def event(self):
        return Event.query.filter(Event.id == self.event_id, Event.organization_id==self.organization.id).first()

class AbstractLotResource(LotResourceBase):
    @property
    def lot(self):
        raise NotImplementedError

    @reify
    def event(self):
        if self.lot:
            return self.lot.event

class LotResource(AbstractLotResource):
    def __init__(self, request):
        super(LotResource, self).__init__(request)
        try:
            self.lot_id = long(self.request.matchdict.get('lot_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound

    @reify
    def lot(self):
        return Lot.query.join(Event).filter(Lot.id==self.lot_id, Event.organization_id==self.organization.id).first()

    @reify
    def lots_cart_url(self):
        cart_url = get_lots_cart_url_builder(self.request).build(self.request, self.event, self.lot)
        return cart_url

    @reify
    def agreement_lots_cart_url(self):
        cart_url = get_agreement_lots_cart_url_builder(self.request).build(self.request, self.event, self.lot)
        return cart_url

    @reify
    def lots_cart_now_url(self):
        return get_cart_now_url_builder(self.request).build(self.request, self.lots_cart_url, self.event.id if self.event else None)

    @reify
    def agreement_lots_cart_now_url(self):
        return get_cart_now_url_builder(self.request).build(self.request, self.agreement_lots_cart_url, self.event.id if self.event else None)


class LotViewResource(LotResource):
    def __init__(self, request, lot_id):
        super(LotResource, self).__init__(request)
        try:
            self.lot_id = long(lot_id)
        except (TypeError, ValueError):
            raise HTTPNotFound

class LotEntryResource(AbstractLotResource):
    def __init__(self, request):
        super(LotEntryResource, self).__init__(request)
        try:
            self.entry_no = self.request.matchdict.get('entry_no')
        except (TypeError, ValueError):
            raise HTTPNotFound

    @reify
    def entry(self):
        return LotEntry.query.join(LotEntry.lot).join(Lot.event).filter(LotEntry.entry_no==self.entry_no, Event.organization_id==self.organization.id).one()

    @reify
    def lot(self):
        return self.entry.lot

class LotProductResource(AbstractLotResource):
    def __init__(self, request):
        super(LotProductResource, self).__init__(request)
        try:
            self.product_id = long(self.request.matchdict.get('product_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound

    @reify
    def lot(self):
        return Lot.query.filter(Lot.has_product(self.product)).one()

    @reify
    def product(self):
        return Product.query.filter(Product.id==self.product_id).one()

class LotEntryReportSettingResource(AbstractLotResource):
    def __init__(self, request):
        super(LotEntryReportSettingResource, self).__init__(request)
        try:
            self.lot_id = long(self.request.matchdict.get('lot_id'))
            self.report_setting_id = long(self.request.matchdict.get('setting_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound

    @reify
    def lot(self):
        obj = None
        try:
            obj = Lot.query.join(Event).filter(Lot.id==self.lot_id, Event.organization_id==self.organization.id).one()
        except NoResultFound:
            raise HTTPNotFound
        return obj

    @reify
    def report_setting(self):
        rs = None
        try:
            rs = LotEntryReportSetting.query.filter(LotEntryReportSetting.id==self.report_setting_id).one()
        except NoResultFound:
            raise HTTPNotFound
        return rs
