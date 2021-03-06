#-*- coding: utf-8 -*-
from pyramid.decorator import reify
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest,
    )
from sqlalchemy import (
    or_,
    and_,
    )
from sqlalchemy.sql.expression import desc
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )
from pyramid.threadlocal import get_current_request
from altair.sqlahelper import get_db_session
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Account,
    Venue,
    AugusVenue,
    Event,
    AugusAccount,
    AugusTicket,
    AugusPerformance,
    AugusStockInfo,
    AugusTicket
    )
from .utils import (
    RequestAccessor,
    )
from .errors import (
    NoSeatError,
    BadRequest,
    )
from .csveditor import (
    AugusCSVEditor,
    )


class AugusVenueListRequestAccessor(RequestAccessor):
    in_matchdict = {'augus_venue_code': int}

class AugusVenueListResource(TicketingAdminResource):
    accessor_factory = AugusVenueListRequestAccessor
    def __init__(self, request):
        super(type(self), self).__init__(request)
        self.accessor = self.accessor_factory(request)

    @reify
    def augus_venue_code(self):
        return self.accessor.augus_venue_code

    @reify
    def augus_venues(self):
        augus_venues = AugusVenue.query.filter(AugusVenue.code==self.augus_venue_code).all()
        if 0 == len(augus_venues):
            raise HTTPNotFound(
                'Not found AugusVenue: AugusVenue.code == {} is not found.'.format(
                    self.augus_venue_code))
        return augus_venues


class AugusVenueRequestAccessor(RequestAccessor):
    in_matchdict = {'augus_venue_code': int,
                    'augus_venue_version': int,
                    }
    in_params = {'augus_account_id': int,
        }


class VenueCommonResource(TicketingAdminResource):
    def __init__(self, request):
        super(VenueCommonResource, self).__init__(request)
        self.__slave_session = get_db_session(get_current_request(), name="slave")

    def get_augus_account_by_id(self, augus_account_id):
        return self.__slave_session.query(AugusAccount)\
            .join(Account)\
            .filter(AugusAccount.id==augus_account_id)\
            .filter(Account.organization_id == self.organization.id)\
            .first()


class AugusVenueResource(VenueCommonResource):
    accessor_factory = AugusVenueRequestAccessor

    def __init__(self, request):
        super(type(self), self).__init__(request)
        self.accessor = self.accessor_factory(request)

    @reify
    def augus_account(self):
        augus_account_id = self.accessor.augus_account_id
        return AugusAccount\
          .query\
          .join(Account)\
          .filter(AugusAccount.id==augus_account_id)\
          .filter(Account.organization_id==self.organization.id)\
          .first()

    @reify
    def augus_venue_code(self):
        return self.accessor.augus_venue_code

    @reify
    def augus_venue_version(self):
        return self.accessor.augus_venue_version

    @reify
    def augus_venue(self):
        try:
            return AugusVenue\
                .query.filter(AugusVenue.code==self.augus_venue_code)\
                      .filter(AugusVenue.version==self.augus_venue_version) \
                      .order_by(desc(AugusVenue.id)).first()
        except (MultipleResultsFound, NoResultFound):
            raise HTTPNotFound('The AugusVenue not found or multiply: code={}, version={}'.format(
                self.augus_venue_code, self.augus_venue_version))

    @staticmethod
    def is_valid_csv_format(header, target_augus_account):
        # TKT5866 AugusAccount設定で整理券フォーマットon/offを見ては入力CSVのフォーマットをチェックする
        # ヘッダ行の項目数で判断する。会場連携ダウンロード・アップロード間の連携先指定誤りを検出する。
        csv_header_expected = AugusCSVEditor(target_augus_account).get_csv_header()
        return len(csv_header_expected) != len(header)

    @staticmethod
    def is_kazuuke_augus_venue(records, headers):
        if len(records) == 1:
            # 自由席のみの会場図は、データが一つのみでブロックNo・座標Y・座標Xが全て0となる
            data = records[0]

            def to_int(col):
                return int(col) if col.strip() else None

            block = to_int(data[headers.index('augus_seat_block')])
            coody = to_int(data[headers.index('augus_seat_coordy')])
            coodx = to_int(data[headers.index('augus_seat_coordx')])

            return (block == 0) and (coody == 0) and (coodx == 0)

        return False


class VenueRequestAccessor(RequestAccessor):
    in_matchdict = {'venue_id': int}

class VenueResource(VenueCommonResource):
    accessor_factory = VenueRequestAccessor

    def __init__(self, request):
        super(type(self), self).__init__(request)
        self.accessor = self.accessor_factory(request)


    @reify
    def venue(self):
        try:
            return Venue.query.filter(Venue.id==self.accessor.venue_id)\
                              .filter(Venue.organization_id==self.organization.id)\
                              .one()
        except (MultipleResultsFound, NoResultFound) as err:
            raise HTTPNotFound('The venue_id = {} is not found or multiply.'.format(self.accessor.venue_id))


    @reify
    def augus_venues(self):
        return AugusVenue.query.filter(AugusVenue.venue_id==self.venue.id).all()


class ChildVenueRequestAccessor(VenueRequestAccessor):
    pass

class ChildVenueResource(TicketingAdminResource):
    accessor_factory = ChildVenueRequestAccessor
    def __init__(self, request):
        super(type(self), self).__init__(request)
        self.accessor = self.accessor_factory(request)


    @reify
    def venue(self):
        try:
            return Venue.query.filter(Venue.id==self.accessor.venue_id)\
                              .filter(Venue.organization_id==self.organization.id)\
                              .one()
        except (MultipleResultsFound, NoResultFound) as err:
            raise HTTPNotFound('The venue_id = {} is not found or multiply.'.format(self.accessor.venue_id))

    @reify
    def parent(self):
        return Venue\
          .query\
          .filter(Venue.site_id==self.venue.site_id)\
          .filter(Venue.performance_id==None)\
          .one()

    @reify
    def augus_venues(self):
        return AugusVenue\
          .query\
          .filter(AugusVenue.venue_id==self.parent.id)\
          .all()


class PerformanceRequestAccessor(RequestAccessor):
    in_matchdict = {'event_id': int}


class PerformanceResource(TicketingAdminResource):
    accessor_factory = PerformanceRequestAccessor

    def __init__(self, request):
        super(type(self), self).__init__(request)
        self.accessor = self.accessor_factory(request)
        self.__slave_session = get_db_session(get_current_request(), name="slave")

    @reify
    def event(self):
        try:
            return Event.query.filter(Event.id==self.accessor.event_id)\
                              .filter(Venue.organization_id==self.organization.id)\
                              .one()
        except (MultipleResultsFound, NoResultFound) as err:
            raise HTTPNotFound('The event_id = {} is not found or multiply.'.format(self.accessor.event_id))

    @reify
    def performances(self):
        return self.event.performances

    @reify
    def augus_performance_all(self):
        try:
            return AugusPerformance.query.all()
        except (MultipleResultsFound, NoResultFound) as err:
            raise HTTPNotFound('The event_id = {} is not found or multiply.'.format(self.accessor.event_id))

    def get_performance_augus_performance_pair(self):
        for performance in self.performances:
            ag_performance = AugusPerformance.get(performance_id=performance.id)
            yield performance, ag_performance

    @reify
    def performance_agperformance(self):
        return [(performance, ag_performance)
                for performance, ag_performance
                in self.get_performance_augus_performance_pair()]

    def get_augus_stock_info_by_stock_types(self, augus_performance_id, stock_type_ids):

        return self.__slave_session.query(AugusStockInfo)\
            .join(AugusTicket, AugusTicket.id == AugusStockInfo.augus_ticket_id)\
            .options(contains_eager(AugusStockInfo.augus_ticket))\
            .filter(AugusStockInfo.augus_performance_id == augus_performance_id,
                    AugusTicket.stock_type_id.in_(stock_type_ids))\
            .all()


class SeatTypeRequestAccessor(RequestAccessor):
    in_matchdict = {'event_id': int}


class SeatTypeResource(TicketingAdminResource):
    accessor_factory = SeatTypeRequestAccessor
    def __init__(self, request):
        super(type(self), self).__init__(request)
        self.accessor = self.accessor_factory(request)

    @reify
    def event(self):
        try:
            return Event.query.filter(Event.id==self.accessor.event_id)\
                              .filter(Venue.organization_id==self.organization.id)\
                              .one()
        except (MultipleResultsFound, NoResultFound) as err:
            raise HTTPNotFound('The event_id = {} is not found or multiply.'.format(self.accessor.event_id))

    @reify
    def ag_tickets(self):
        performance_ids = [pfc.id for pfc in self.event.performances]
        ag_performance_ids = [ag_performance.id
                              for ag_performance in AugusPerformance.query.filter(AugusPerformance.performance_id.in_(performance_ids)).all()]
        ag_tickets = AugusTicket.query.filter(AugusTicket.augus_performance_id.in_(ag_performance_ids)).all()
        return ag_tickets
