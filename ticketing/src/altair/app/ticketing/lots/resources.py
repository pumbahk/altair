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

from altair.app.ticketing.core.models import Event, Performance, Organization, ShippingAddress
from altair.app.ticketing.core import api as core_api
from .exceptions import OutTermException, OverEntryLimitException, OverEntryLimitPerPerformanceException
from .models import Lot, LotEntry, LotEntryWish


logger = logging.getLogger(__name__)

def lot_resource_factory(request):
    if request.matchdict is None:
        return DefaultRootFactory(request)

    context = LotResource(request)
    if not context.lot:
        raise HTTPNotFound

    if context.lot:
        if not context.lot.available_on(datetime.now()):
            raise OutTermException(lot_name=context.lot.name,
                                   from_=context.lot.start_at,
                                   to_=context.lot.end_at)
    return context



class LotResource(object):
    def __init__(self, request):
        self.request = request

        self.organization = core_api.get_organization(self.request)

        event_id = self.request.matchdict.get('event_id')
        self.event = Event.query \
            .filter(Event.id==event_id) \
            .filter(Organization.id==self.organization.id) \
            .first()

        lot = None 
        if self.event is not None: 
            lot_id = self.request.matchdict.get('lot_id')
            lot = Lot.query \
                .filter(Lot.event_id==event_id) \
                .filter(Lot.id==lot_id) \
                .first()
        self.lot = lot

    def authenticated_user(self):
        from altair.rakuten_auth.api import authenticated_user
        user = authenticated_user(self.request)
        return user or { 'is_guest': True }

    @reify
    def host_base_url(self):
        return core_api.get_host_base_url(self.request)

    @reify
    def __acl__(self):
        logger.debug('acl: lot %s' % self.lot)
        if not self.lot:
            logger.debug('acl: lot is not found')
            return []

        if not self.lot.auth_type:
            logger.debug('acl: lot has no auth_type')
            return [
                (Allow, Everyone, 'lots'),
            ]

        logger.debug('acl: lot has acl to auth_type:%s' % self.lot.auth_type)
        return [
            (Allow, "auth_type:%s" % self.lot.auth_type, 'lots'),
        ]

    def check_entry_limit(self, user, email, wishes):
        query = LotEntry.query.filter(LotEntry.lot_id==self.lot.id, LotEntry.canceled_at==None)
        if user:
            query = query.filter(LotEntry.user_id==user.id)
        elif email:
            query = query.join(Shipping_address)\
                         .filter(or_(ShippingAddress.email_1==email, ShippingAddress.email_2==email))
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
