# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from zope.interface import implementer
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import (
    Everyone,
    Allow,
    DENY_ALL,
)
from pyramid.traversal import DefaultRootFactory
from pyramid.decorator import reify
from sqlalchemy.sql import or_
from sqlalchemy.orm import make_transient, joinedload

from altair.now import get_now
from altair.app.ticketing.cart.api import get_auth_info
from altair.app.ticketing.core.models import Event, Performance, Organization, ShippingAddress, SalesSegment, SalesSegmentGroup
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.users import models as u_models
from altair.sqlahelper import get_db_session

from .interfaces import ILotResource
from .exceptions import OutTermException, OverEntryLimitException, OverEntryLimitPerPerformanceException
from .models import Lot, LotEntry, LotEntryWish
from .api import get_lot_entry_dict

logger = logging.getLogger(__name__)

def lot_resource_factory(request):
    if request.matchdict is None:
        return DefaultRootFactory(request)

    context = LotResource(request)
    lot = context.lot
    if not lot:
        raise HTTPNotFound

    if not lot.available_on(context.now):
        make_transient(lot)
        raise OutTermException(lot=lot)
    return context


class LotResourceBase(object):
    lot = None

    @property
    def event(self):
        return self.lot and self.lot.event

    def authenticated_user(self):
        return get_auth_info(self.request)

    @reify
    def cart_setting(self):
        return self.event.setting.cart_setting or self.event.organization.setting.cart_setting

    @reify
    def host_base_url(self):
        return core_api.get_host_base_url(self.request)

    @reify
    def __acl__(self):
        logger.debug('acl: lot %s' % self.lot.id)
        acl = []
        if self.lot:
            if not self.lot.auth_type:
                acl.append((Allow, Everyone, 'lots'))
            else:
                required_principals = set()
                guest_exists = False
                try:
                    for membergroup in self.lot.sales_segment.membergroups:
                        if membergroup.is_guest:
                            required_principals.add('membership:%s' % membergroup.membership.name)
                        else: 
                            required_principals.add('membergroup:%s' % membergroup.name)
                    effective_principals = self.request.effective_principals
                    logger.debug('required principals: %r, provided: %r' % (required_principals, effective_principals))
                    logger.debug('acl: lot has acl to auth_type:%s' % self.lot.auth_type)
                    if not required_principals.isdisjoint(effective_principals):
                        logger.debug('granting access to auth_type:%s' % self.lot.auth_type)
                        acl.append((Allow, "altair.auth.authenticator:%s" % self.lot.auth_type, 'lots'))
                    else:
                        logger.debug('no access granted')
                except:
                    logger.exception('WTF?')
        acl.append(DENY_ALL)
        return acl

    @property
    def membershipinfo(self):
        return cart_api.get_membership(self.authenticated_user())


@implementer(ILotResource)
class LotResource(LotResourceBase):
    def __init__(self, request):
        self.request = request
        self.now = get_now(request)

        self.organization = self.request.organization
        lot_entry_dict = get_lot_entry_dict(self.request)
        lot_id_from_session = lot_entry_dict and lot_entry_dict['lot_id']
        lot_id = None
        try:
            lot_id = long(self.request.matchdict.get('lot_id'))
        except (TypeError, ValueError):
            pass
        if lot_id is None:
            lot_id = lot_id_from_session
        else:
            if lot_id_from_session is not None and lot_id != lot_id_from_session:
                logger.info('lot_id (%ld) != lot_id_from_session (%ld)' % (lot_id, lot_id_from_session))
                raise HTTPNotFound()
        event_id = None
        try:
            event_id = long(self.request.matchdict.get('event_id'))
        except (TypeError, ValueError):
            pass
        self._event_id = event_id
        self._lot_id = lot_id

    @reify
    def lot(self):
        lot = Lot.query \
            .options(joinedload(Lot.event)) \
            .join(Lot.event) \
            .filter(Event.organization_id == self.organization.id) \
            .filter(Lot.id == self._lot_id) \
            .first()
        if not lot:
            return None
        if self._event_id is not None and lot.event_id != self._event_id:
            return None
        return lot

    @reify
    def lot_asid(self):
        organization = cart_api.get_organization(self.request)
        lot_asid =organization.setting.lot_asid
        logger.debug('organization %s' % organization.code)
        logger.debug('lot_asid %s' % lot_asid)
        return lot_asid

    def check_entry_limit(self, wishes, user=None, email=None):
        logger.debug('user.id=%r, email=%r', user.id if user else None, email)
        query = LotEntry.query.filter(LotEntry.lot_id==self.lot.id, LotEntry.canceled_at==None)
        if user:
            query = query.filter(LotEntry.user_id==user.id)
        elif email:
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

class LotReviewResource(LotResourceBase):
    def __init__(self, request):
        self.request = request
        self.organization = self.request.organization


@implementer(ILotResource)
class LotLogoutResource(LotResourceBase):
    def __init__(self, request):
        self.request = request
        self.organization = self.request.organization
        self._lot_id = request.params.get("lot_id", None)

    @reify
    def lot(self):
        lot = Lot.query \
            .options(joinedload(Lot.event)) \
            .join(Lot.event) \
            .filter(Event.organization_id == self.organization.id) \
            .filter(Lot.id == self._lot_id) \
            .first()
        if not lot:
            return None
        return lot

    @reify
    def _event_id(self):
        return self.lot.event_id
