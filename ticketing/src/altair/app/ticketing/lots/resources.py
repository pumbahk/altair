# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import (
    Everyone,
    Allow,
)
from pyramid.traversal import DefaultRootFactory
from pyramid.decorator import reify
from sqlalchemy.sql import or_
from sqlalchemy.orm import make_transient, joinedload

from altair.now import get_now
from altair.app.ticketing.cart.api import get_auth_info 
from altair.app.ticketing.core.models import Event, Performance, Organization, ShippingAddress
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.cart import api as cart_api

from .exceptions import OutTermException, OverEntryLimitException, OverEntryLimitPerPerformanceException
from .models import Lot, LotEntry, LotEntryWish

logger = logging.getLogger(__name__)

def lot_resource_factory(request):
    if request.matchdict is None:
        return DefaultRootFactory(request)

    context = LotResource(request)
    lot = context.lot
    if not lot:
        raise HTTPNotFound

    if not lot.available_on(get_now(request)):
        make_transient(lot)
        raise OutTermException(lot=lot)
    return context



class LotResource(object):
    def __init__(self, request):
        self.request = request

        self.organization = cart_api.get_organization(self.request)

        event_id = self.request.matchdict.get('event_id')
        lot_id = self.request.matchdict.get('lot_id')
        lot = Lot.query \
            .options(joinedload(Lot.event)) \
            .join(Lot.event) \
            .filter(Event.organization_id == self.organization.id) \
            .filter(Lot.event_id==event_id) \
            .filter(Lot.id==lot_id) \
            .first()
        self.lot = lot
        self.event = lot and lot.event

        # for B/W compatibility
        self.nogizaka_lot_ids = set(long(c) for c in (c.strip() for c in request.registry.settings.get('altair.lots.nogizaka_lot_id', '').split(',')) if c)

    def authenticated_user(self):
        return get_auth_info(self.request)

    @reify
    def host_base_url(self):
        return core_api.get_host_base_url(self.request)

    @reify
    def __acl__(self):
        logger.debug('acl: lot %s' % self.lot)
        if not self.lot:
            logger.debug('acl: lot is not found')
            return []

        if not self.auth_type:
            logger.debug('acl: lot has no auth_type')
            return [
                (Allow, Everyone, 'lots'),
            ]

        logger.debug('acl: lot has acl to auth_type:%s' % self.lot.auth_type)
        return [
            (Allow, "auth_type:%s" % self.auth_type, 'lots'),
        ]

    @reify
    def auth_type(self):
        # for B/W compatibility
        if self.lot.id in self.nogizaka_lot_ids:
            return 'nogizaka46'
        return self.lot.auth_type

    def check_entry_limit(self, wishes, user=None, email=None):
        query = LotEntry.query.filter(LotEntry.lot_id==self.lot.id, LotEntry.canceled_at==None)
        if email:
            query = query.join(ShippingAddress)\
                         .filter(or_(ShippingAddress.email_1==email, ShippingAddress.email_2==email))
        else:
            return
        # 抽選単位での申込上限チェック
        entry_limit = self.lot.entry_limit
        if entry_limit > 0:
            entry_count = query.count()
            logger.info('Lot(id=%d): entry_limit=%r, entries=%d' % (self.lot.id, entry_limit, entry_count))
            if entry_count >= entry_limit:
                logger.info('entry_limit exceeded')
                raise OverEntryLimitException(entry_limit=entry_limit)
        # 公演単位での申込上限チェック
        for wish_data in wishes:
            performance = Performance.get(wish_data.get('performance_id'), self.organization.id)
            entry_limit = performance.setting.entry_limit
            if entry_limit > 0:
                query_performance = query.join(LotEntryWish).filter(LotEntryWish.performance_id==performance.id)
                entry_count = query_performance.count()
                logger.info('Performance(id=%d): entry_limit=%r, entries=%d' % (performance.id, entry_limit, entry_count))
                if entry_count >= entry_limit:
                    logger.info('entry_limit exceeded')
                    raise OverEntryLimitPerPerformanceException(performance_name=performance.name, entry_limit=entry_limit)

class LotOptionSelectionResource(LotResource):
    def __init__(self, request):
        super(LotOptionSelectionResource, self).__init__(request)
        option_index = None
        try:
            option_index = int(self.request.matchdict.get('option_index'))
        except (TypeError, ValueError):
            pass
        if option_index is None:
            try:
                option_index = int(self.request.params.get('option_index'))
            except (TypeError, ValueError):
                pass
        if option_index > self.lot.limit_wishes:
            option_index = None
        self.option_index = option_index

        performance_id = None
        try:
            performance_id = int(self.request.params.get('performance_id'))
        except (ValueError, TypeError):
            pass

        self.performance = Performance.query \
            .filter(Performance.id == performance_id) \
            .filter(Performance.event_id == self.event.id) \
            .first()
