# -*- coding: utf-8 -*-
import sys
import logging
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from datetime import datetime
from altair.sqlahelper import get_db_session
import functools
from .models import (
    FamiPortOrder,
    FamiPortTicket,
    FamiPortClient,
    FamiPortVenue,
    FamiPortEvent,
    FamiPortPerformance,
    FamiPortPerformanceType,
    FamiPortPrefecture,
    FamiPortReceipt,
    FamiPortOrderType,
    FamiPortReceiptType,
    FamiPortSalesSegment,
    FamiPortGenre1,
    FamiPortGenre2,
    FamiPortSalesChannel,
    FamiPortBarcodeNoSequence,
    FamiPortReserveNumberSequence,
    FamiPortOrderTicketNoSequence,
    FamiPortOrderIdentifierSequence,
    FamiPortExchangeTicketNoSequence,
    )
from .exc import (
    FamiPortAPIError, 
    FamiPortAPINotFoundError,
    FamiportPaymentDateNoneError,
    FamiPortTicketingDateNoneError,
    FamiPortAlreadyPaidError
)
from .communication.api import (  # noqa
    get_response_builder,  # noqa B/W compatibility
    get_xmlResponse_generator,  # noqa B/W compatibility
    )
from . import internal_api as internal

logger = logging.getLogger(__name__)

Unspecified = ['Unspecified']

def user_api(fn):
    def _(*args, **kwargs):
        return fn(*args, **kwargs)
    functools.update_wrapper(_, fn)
    return _


def famiport_venue_to_dict(famiport_venue):
    return dict(
        venue_id=famiport_venue.id,
        userside_id=famiport_venue.userside_id,
        client_code=famiport_venue.client_code,
        name=famiport_venue.name,
        name_kana=famiport_venue.name_kana,
        prefecture=famiport_venue.prefecture
        )

def famiport_sales_segment_to_dict(famiport_sales_segment):
    famiport_performance = famiport_sales_segment.famiport_performance
    famiport_event = famiport_performance.famiport_event
    return dict(
        client_code=famiport_event.client_code,
        event_code_1=famiport_event.code_1,
        event_code_2=famiport_event.code_2,
        performance_code=famiport_performance.code,
        code=famiport_sales_segment.code,
        name=famiport_sales_segment.name,
        sales_channel=famiport_sales_segment.sales_channel,
        published_at=famiport_sales_segment.published_at,
        start_at=famiport_sales_segment.start_at,
        end_at=famiport_sales_segment.end_at,
        auth_required=famiport_sales_segment.auth_required,
        auth_message=famiport_sales_segment.auth_message,
        seat_selection_start_at=famiport_sales_segment.seat_selection_start_at
        )

def famiport_performance_to_dict(famiport_performance):
    famiport_event = famiport_performance.famiport_event
    return dict(
        client_code=famiport_event.client_code,
        event_code_1=famiport_event.code_1,
        event_code_2=famiport_event.code_2,
        code=famiport_performance.code,
        name=famiport_performance.name,
        type=famiport_performance.type,
        searchable=famiport_performance.searchable,
        sales_channel=famiport_performance.sales_channel,
        start_at=famiport_performance.start_at,
        ticket_name=famiport_performance.ticket_name,
        )

def famiport_event_to_dict(famiport_event):
    return dict(
        client_code=famiport_event.client_code,
        code_1=famiport_event.code_1,
        code_2=famiport_event.code_2,
        name_1=famiport_event.name_1,
        name_2=famiport_event.name_2,
        sales_channel=famiport_event.sales_channel,
        venue_id=famiport_event.venue_id,
        purchasable_prefectures=famiport_event.purchasable_prefectures,
        start_at=famiport_event.start_at,
        end_at=famiport_event.end_at,
        genre_1_code=famiport_event.genre_1_code,
        genre_2_code=famiport_event.genre_2_code,
        keywords=famiport_event.keywords,
        search_code=famiport_event.search_code
        )

def famiport_order_to_dict(famiport_order):
    payment_reserve_number = None
    ticketing_reserve_number = None
    payment_shop_name = None
    ticketing_shop_name = None
    for famiport_receipt in famiport_order.famiport_receipts:
        if famiport_receipt.type in (FamiPortReceiptType.CashOnDelivery.value, FamiPortReceiptType.Payment.value):
            payment_reserve_number = famiport_receipt.reserve_number
            payment_shop_name = famiport_receipt.shop.name if famiport_receipt.shop is not None else famiport_receipt.shop_code
        elif famiport_receipt.type == FamiPortReceiptType.Ticketing.value:
            ticketing_reserve_number = famiport_receipt.reserve_number
            ticketing_shop_name = famiport_receipt.shop.name if famiport_receipt.shop is not None else famiport_receipt.shop_code
        else:
            raise AssertionError('?')
    if famiport_order.type == FamiPortOrderType.Ticketing.value:
        payment_reserve_number = ticketing_reserve_number
    elif famiport_order.type == FamiPortOrderType.CashOnDelivery.value:
        ticketing_reserve_number = payment_reserve_number

    retval = dict(
        type=famiport_order.type,
        order_no=famiport_order.order_no,
        famiport_order_identifier=famiport_order.famiport_order_identifier,
        customer_name=famiport_order.customer_name,
        customer_phone_number=famiport_order.customer_phone_number,
        customer_address_1=famiport_order.customer_address_1,
        customer_address_2=famiport_order.customer_address_2,
        total_amount=famiport_order.total_amount,
        ticket_payment=famiport_order.ticket_payment,
        system_fee=famiport_order.system_fee,
        ticketing_fee=famiport_order.ticketing_fee,
        ticketing_start_at=famiport_order.ticketing_start_at,
        ticketing_end_at=famiport_order.ticketing_end_at,
        payment_start_at=famiport_order.payment_start_at,
        payment_due_at=famiport_order.payment_due_at,
        paid_at=famiport_order.paid_at,
        issued_at=famiport_order.issued_at,
        canceled_at=famiport_order.canceled_at,
        payment_reserve_number=payment_reserve_number,
        ticketing_reserve_number=ticketing_reserve_number,
        payment_shop_name=payment_shop_name,
        ticketing_shop_name=ticketing_shop_name,
        famiport_tickets=[
            dict(
                type=famiport_ticket.type,
                barcode_number=famiport_ticket.barcode_number,
                template=famiport_ticket.template_code,
                data=famiport_ticket.data,
                subticket=famiport_ticket.is_subticket,
                userside_token_id=famiport_ticket.userside_token_id,
                logically_subticket=famiport_ticket.logically_subticket
                )
            for famiport_ticket in famiport_order.famiport_tickets
            ]
        )
    assert famiport_order.famiport_performance is not None
    performance_dict = famiport_performance_to_dict(famiport_order.famiport_performance)
    if famiport_order.famiport_sales_segment is not None:
        sales_segment_dict = famiport_sales_segment_to_dict(famiport_order.famiport_sales_segment)
        sales_segment_code = sales_segment_dict['code']
    else:
        sales_segment_code = None
    retval.update(
        event_code_1=performance_dict['event_code_1'],
        event_code_2=performance_dict['event_code_2'],
        performance_code=performance_dict['code'],
        sales_segment_code=sales_segment_code
        )
    return retval

@user_api
def get_famiport_order(request, client_code, order_no):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_order = internal.get_famiport_order(session, client_code, order_no)
        return famiport_order_to_dict(famiport_order)
    except NoResultFound:
        raise FamiPortAPINotFoundError('no such order: %s' % order_no)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_order_by_reserve_number(request, reserve_number):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_order = session.query(FamiPortOrder).join(FamiPortReceipt, FamiPortReceipt.famiport_order_id == FamiPortOrder.id)\
                                                     .filter(FamiPortReceipt.reserve_number == reserve_number).one()
        return famiport_order_to_dict(famiport_order)
    except NoResultFound:
        raise FamiPortAPINotFoundError('no such order corresponds to reserve_number: %s' % reserve_number)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')


@user_api
def get_famiport_venue_by_name(request, client_code, name):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_venue = internal.get_famiport_venue_by_name(session, client_code, name)
        return famiport_venue_to_dict(famiport_venue)
    except NoResultFound:
        raise FamiPortAPINotFoundError('no such venue corresponds to name: %s' % name)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_venue_by_userside_id(request, client_code, userside_id):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_venue = internal.get_famiport_venue_by_userside_id(session, client_code, userside_id)
        return famiport_venue_to_dict(famiport_venue)
    except NoResultFound:
        raise FamiPortAPINotFoundError('no such venue corresponds to userside_id: %d' % userside_id)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_venue_by_userside_id_or_name(request, client_code, userside_id, name):
    sys.exc_clear()
    try:
        return get_famiport_venue_by_userside_id(request, client_code, userside_id)
    except FamiPortAPINotFoundError:
        return get_famiport_venue_by_name(request, client_code, name)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_sales_segment_by_userside_id(request, client_code, userside_id):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_sales_segment = internal.get_famiport_sales_segment_by_userside_id(session, client_code, userside_id)
        return famiport_sales_segment_to_dict(famiport_sales_segment)
    except NoResultFound:
        raise FamiPortAPINotFoundError('no such sales_segment corresponds to userside_id: %d' % userside_id)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_performance_by_userside_id(request, client_code, userside_id):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_performance = internal.get_famiport_performance_by_userside_id(session, client_code, userside_id)
        return famiport_performance_to_dict(famiport_performance)
    except NoResultFound:
        raise FamiPortAPINotFoundError('no such performance corresponds to userside_id: %d' % userside_id)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_event_by_userside_id(request, client_code, userside_id):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_event = internal.get_famiport_event_by_userside_id(session, client_code, userside_id)
        return famiport_event_to_dict(famiport_event)
    except NoResultFound:
        raise FamiPortAPINotFoundError('no such event corresponds to userside_id: %d' % userside_id)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def create_or_get_famiport_venue(request, client_code, userside_id, name, name_kana, prefecture):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')

        # validation
        internal.get_famiport_client(session, client_code)
        # validation
        internal.validate_prefecture(prefecture)

        famiport_venue = None
        famiport_venue = session.query(FamiPortVenue) \
            .filter(FamiPortVenue.client_code == client_code) \
            .filter(FamiPortVenue.userside_id == userside_id) \
            .filter(FamiPortVenue.name == name) \
            .filter(FamiPortVenue.prefecture == prefecture).first()
        if famiport_venue == None:
            famiport_venue = FamiPortVenue(client_code = client_code, userside_id = userside_id, \
                                           name = name, name_kana = name_kana, prefecture = prefecture)
            session.add(famiport_venue)
            session.commit()
        return dict(venue_id=famiport_venue.id)

    except FamiPortAPIError as famiPortAPIError:
        raise famiPortAPIError
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def create_or_update_famiport_venue(
        request,
        client_code,
        id,
        userside_id,
        name,
        name_kana,
        prefecture,
        update_existing=True):
    sys.exc_clear()
    new = False
    try:
        session = get_db_session(request, 'famiport')

        # validation
        internal.get_famiport_client(session, client_code)

        # validation
        internal.validate_prefecture(prefecture)

        venue = None
        try:
            if id is not None:
                venue = session.query(FamiPortVenue) \
                    .filter(FamiPortVenue.client_code == client_code) \
                    .filter(FamiPortVenue.id == id) \
                    .one()
            else:
                venue = session.query(FamiPortVenue) \
                    .filter(FamiPortVenue.client_code == client_code) \
                    .filter(FamiPortVenue.name == name) \
                    .one()
        except NoResultFound:
            pass
        except MultipleResultsFound:
            raise FamiPortAPIError('internal error')
        sys.exc_clear()

        if not update_existing and venue is not None:
            raise FamiPortAPIError('venue already exists')
        if venue is None:
            venue = FamiPortVenue(client_code=client_code)
            new = True
            session.add(venue)

        venue.userside_id = userside_id
        venue.name = name
        venue.name_kana = name_kana
        venue.prefecture = prefecture

        session.commit()
        return dict(
            new=new,
            venue_id=venue.id
            )
    except FamiPortAPIError:
        raise
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error', client_code)


@user_api
def create_or_update_famiport_event(
        request,
        client_code,
        userside_id,
        code_1,
        code_2,
        name_1,
        name_2,
        sales_channel,
        venue_id,
        purchasable_prefectures,
        start_at,
        end_at,
        genre_1_code,
        genre_2_code,
        keywords,
        search_code,
        update_existing=False,
        now=None):
    sys.exc_clear()
    try:
        if now is None:
            now = datetime.now()
        session = get_db_session(request, 'famiport')

        # validate
        internal.get_famiport_client(session, client_code)

        try:
            venue = session.query(FamiPortVenue) \
                .filter_by(client_code=client_code) \
                .filter_by(id=venue_id) \
                .one()
        except NoResultFound:
            raise FamiPortAPINotFoundError('no corresponding venue found for id=%ld' % venue_id)

        genre_1 = None
        if genre_1_code is not None and genre_1_code != u'':
            try:
                genre_1 = session.query(FamiPortGenre1) \
                    .filter_by(code=genre_1_code) \
                    .one()
            except NoResultFound:
                raise FamiPortAPINotFoundError('no corresponding genre found for code=%s' % genre_1_code)

        genre_2 = None
        if genre_2_code is not None and genre_2_code != u'':
            try:
                genre_2 = session.query(FamiPortGenre2) \
                    .filter_by(code=genre_2_code) \
                    .one()
            except NoResultFound:
                raise FamiPortAPINotFoundError('no corresponding subgenre found for code=%s' % genre_2_code)

        old_event = None
        try:
            old_event = session.query(FamiPortEvent) \
                .with_lockmode('update') \
                .filter(FamiPortEvent.client_code == client_code) \
                .filter(FamiPortEvent.code_1 == code_1) \
                .filter(FamiPortEvent.code_2 == code_2) \
                .filter(FamiPortEvent.invalidated_at == None) \
                .one()
        except NoResultFound:
            pass
        sys.exc_clear()

        internal.validate_sales_channel(sales_channel)

        if not update_existing and old_event is not None:
            raise FamiPortAPIError(u'event already exists')

        event = FamiPortEvent(
            client_code=client_code,
            code_1=code_1,
            code_2=code_2,
            name_1=name_1,
            name_2=name_2,
            sales_channel=sales_channel,
            venue_id=venue_id,
            userside_id=userside_id,
            genre_1_code=genre_1.code if genre_1 is not None else None,
            genre_2_code=genre_2.code if genre_2 is not None else None,
            keywords=keywords,
            search_code=search_code
            )

        if purchasable_prefectures is not None:
            _purchasable_prefectures = []
            for prefecture_id in purchasable_prefectures:
                if isinstance(prefecture_id, int):
                    pass
                elif isinstance(prefecture_id, (basestring, long)):
                    prefecture_id = int(prefecture_id)
                elif isinstance(prefecture_id, FamiPortPrefecture):
                    prefecture_id = prefecture_id.id
                else:
                    raise FamiPortAPIError('invalid prefecture id: %r' % prefecture_id)
                if prefecture_id == FamiPortPrefecture.Nationwide.id:
                    # 「全国」が一つでも含まれていたら、他の都道府県のことは忘れる
                    purchasable_prefectures = ['%d' % FamiPortPrefecture.Nationwide.id]
                    break
                internal.validate_prefecture(prefecture_id)
                _purchasable_prefectures.append(u'%d' % prefecture_id)
            event.purchasable_prefectures = purchasable_prefectures
        else:
            event.purchasable_prefectures = ['%d' % FamiPortPrefecture.Nationwide.id]
        if keywords is not None:
            event.keywords = keywords

        if old_event is not None:
            event.revision = old_event.revision + 1
            old_event.invalidated_at = now

        session.add(event)
        session.commit()
        return dict(
            new=old_event is None
            )
    except FamiPortAPIError:
        raise
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error', client_code)

@user_api
def create_or_update_famiport_performance(
        request,
        client_code,
        userside_id,
        event_code_1,
        event_code_2,
        code,
        name,
        type_,
        searchable,
        sales_channel,
        start_at,
        ticket_name,
        update_existing=False,
        now=None):
    sys.exc_clear()
    try:
        if now is None:
            now = datetime.now()
        session = get_db_session(request, 'famiport')

        internal.get_famiport_client(session, client_code)

        try:
            event = session.query(FamiPortEvent) \
                .filter(FamiPortEvent.client_code == client_code) \
                .filter(FamiPortEvent.code_1 == event_code_1) \
                .filter(FamiPortEvent.code_2 == event_code_2) \
                .filter(FamiPortEvent.invalidated_at == None) \
                .one()
        except NoResultFound:
            raise FamiPortAPINotFoundError('no corresponding event found for client_code=%s, event_code_1=%s, event_code_2=%s' % (client_code, event_code_1, event_code_2))

        old_performance = None
        try:
            old_performance = session.query(FamiPortPerformance) \
                .with_lockmode('update') \
                .filter(FamiPortPerformance.code == code) \
                .filter(FamiPortPerformance.famiport_event_id == event.id) \
                .filter(FamiPortPerformance.invalidated_at == None) \
                .one()
        except NoResultFound:
            try:
                # When old_performance is moved to another famiport_event
                old_performance = session.query(FamiPortPerformance) \
                    .with_lockmode('update') \
                    .filter(FamiPortPerformance.famiport_event_id == event.id) \
                    .filter(FamiPortPerformance.userside_id == userside_id) \
                    .filter(FamiPortPerformance.invalidated_at == None) \
                    .one()
            except NoResultFound:
                pass
        sys.exc_clear()

        if type_ == FamiPortPerformanceType.Normal.value:
            if ticket_name is not None:
                raise FamiPortAPIError('ticket_name is supplied while type_ == FamiPortPerformanceType.Normal')
        elif type_ == FamiPortPerformanceType.Spanned.value:
            if ticket_name is None:
                raise FamiPortAPIError('ticket_name is not supplied while type_ == FamiPortPerformanceType.Spanned')
        else:
            raise FamiPortAPIError('invalid performance type (%d)' % type_)

        internal.validate_sales_channel(sales_channel)

        if not update_existing and old_performance is not None:
            raise FamiPortAPIError(u'performance already exists')

        performance = FamiPortPerformance(
            code=code,
            famiport_event_id=event.id,
            name=name,
            type=type_,
            searchable=searchable,
            sales_channel=sales_channel,
            ticket_name=ticket_name,
            userside_id=userside_id,
            start_at=start_at
            )
        if old_performance is not None:
            performance.revision = old_performance.revision + 1
            old_performance.invalidated_at = now

        session.add(performance)
        session.commit()
        return dict(
            new=old_performance is None
            )
    except FamiPortAPIError:
        raise
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error', client_code)


@user_api
def create_or_update_famiport_sales_segment(
        request,
        client_code,
        userside_id,
        event_code_1,
        event_code_2,
        performance_code,
        code,
        name,
        sales_channel,
        published_at,
        start_at,
        end_at,
        auth_required,
        auth_message,
        seat_selection_start_at,
        update_existing=False,
        now=None):
    sys.exc_clear()
    new = False
    try:
        if now is None:
            now = datetime.now()
        session = get_db_session(request, 'famiport')

        internal.get_famiport_client(session, client_code)

        try:
            performance = session.query(FamiPortPerformance) \
                .join(FamiPortPerformance.famiport_event) \
                .filter(FamiPortEvent.client_code == client_code) \
                .filter(FamiPortEvent.code_1 == event_code_1) \
                .filter(FamiPortEvent.code_2 == event_code_2) \
                .filter(FamiPortPerformance.code == performance_code) \
                .filter(FamiPortEvent.invalidated_at == None) \
                .filter(FamiPortPerformance.invalidated_at == None) \
                .one()
        except NoResultFound:
            raise FamiPortAPINotFoundError('no corresponding performance found for client_code=%s, event_code_1=%s, event_code_2=%s, performance_code=%s' % (client_code, event_code_1, event_code_2, performance_code))

        old_sales_segment = None
        try:
            old_sales_segment = session.query(FamiPortSalesSegment) \
                .with_lockmode('update') \
                .filter(FamiPortSalesSegment.code == code) \
                .filter(FamiPortSalesSegment.famiport_performance_id == performance.id) \
                .filter(FamiPortSalesSegment.name == name) \
                .filter(FamiPortSalesSegment.start_at == start_at) \
                .filter(FamiPortSalesSegment.end_at == end_at) \
                .filter(FamiPortSalesSegment.invalidated_at == None) \
                .one()
        except NoResultFound:
            try:
                # When old_sales_segment is moved to another famiport_performance
                old_sales_segment = session.query(FamiPortSalesSegment) \
                    .with_lockmode('update') \
                    .filter(FamiPortSalesSegment.famiport_performance_id == performance.id) \
                    .filter(FamiPortSalesSegment.userside_id == userside_id) \
                    .filter(FamiPortSalesSegment.invalidated_at == None) \
                    .one()
            except NoResultFound:
                pass
        sys.exc_clear()

        internal.validate_sales_channel(sales_channel)

        if not update_existing and old_sales_segment is not None:
            raise FamiPortAPIError(u'sales_segment already exists')

        sales_segment = FamiPortSalesSegment(
            code=code,
            famiport_performance_id=performance.id,
            userside_id=userside_id,
            name=name,
            sales_channel=sales_channel,
            published_at=published_at,
            start_at=start_at,
            end_at=end_at,
            auth_required=auth_required,
            auth_message=auth_message,
            seat_selection_start_at=seat_selection_start_at
            )
        if old_sales_segment is not None:
            sales_segment.revision = old_sales_segment.revision + 1
            old_sales_segment.invalidated_at = now

        session.add(sales_segment)
        session.commit()
        return dict(
            new=old_sales_segment is None
            )
    except FamiPortAPIError:
        raise
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error', client_code)


@user_api
def create_famiport_order(
        request,
        client_code,
        type_,
        event_code_1,
        event_code_2,
        performance_code,
        sales_segment_code,
        order_no,
        customer_name,
        customer_phone_number,
        customer_address_1,
        customer_address_2,
        total_amount,
        system_fee,
        ticketing_fee,
        ticket_payment,
        tickets,
        payment_start_at=None,
        payment_due_at=None,
        ticketing_start_at=None,
        ticketing_end_at=None,
        payment_sheet_text=None):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        if sales_segment_code is not None:
            famiport_sales_segment = internal.get_famiport_sales_segment_by_code(
                session,
                client_code=client_code,
                event_code_1=event_code_1,
                event_code_2=event_code_2,
                performance_code=performance_code,
                code=sales_segment_code
                )
            famiport_performance = famiport_sales_segment.famiport_performance
        else:
            famiport_sales_segment = None
            famiport_performance = internal.get_famiport_performance_by_code(
                session,
                client_code=client_code,
                event_code_1=event_code_1,
                event_code_2=event_code_2,
                code=performance_code,
                )
        famiport_order = internal.create_famiport_order(
            session,
            client_code=client_code,
            type_=type_,
            famiport_sales_segment=famiport_sales_segment,
            famiport_performance=famiport_performance,
            order_no=order_no,
            customer_name=customer_name,
            customer_phone_number=customer_phone_number,
            customer_address_1=customer_address_1,
            customer_address_2=customer_address_2,
            total_amount=total_amount,
            system_fee=system_fee,
            ticketing_fee=ticketing_fee,
            ticket_payment=ticket_payment,
            tickets=tickets,
            payment_start_at=payment_start_at,
            payment_due_at=payment_due_at,
            ticketing_start_at=ticketing_start_at,
            ticketing_end_at=ticketing_end_at,
            payment_sheet_text=payment_sheet_text
            )
        return famiport_order_to_dict(famiport_order)
    except FamiPortAPIError:
        raise
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error', client_code)

def do_order(*args, **kwds):
    return create_famiport_order(*args, **kwds)

@user_api
def get_genre_1_list(request):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        return [
            dict(
                code=genre_1.code,
                name=genre_1.name
                )
            for genre_1 in session.query(FamiPortGenre1)
            ]
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_genre_2_list(request):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        return [
            dict(
                code=genre_2.code,
                name=genre_2.name
                )
            for genre_2 in session.query(FamiPortGenre2)
            ]
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

name_to_prefecture_map = dict(
    (prefecture.name, prefecture)
    for prefecture in FamiPortPrefecture
    )

@user_api
def resolve_famiport_prefecture_by_name(request, name):
    try:
        return name_to_prefecture_map[name].id
    except KeyError:
        raise FamiPortAPINotFoundError(u'no such prefecture: %s' % name)


@user_api
def can_cancel_famiport_order(request, client_code, order_no, now=None):
    sys.exc_clear()
    try:
        if now is None:
            now = datetime.now()
        session = get_db_session(request, 'famiport')
        return internal.can_cancel_famiport_order(request, session, client_code, order_no, now)
    except:
        logger.exception(u'internal error')
        return False


@user_api
def cancel_famiport_order_by_order_no(request, client_code, order_no, now=None):
    sys.exc_clear()
    try:
        if now is None:
            now = datetime.now()
        session = get_db_session(request, 'famiport')
        internal.cancel_famiport_order_by_order_no(request, session, client_code, order_no, now)
        session.commit()
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def make_suborder_by_order_no(
        request,
        order_no,
        type_=None,
        reason=None,
        cancel_reason_code=None,
        cancel_reason_text=None,
        client_code=None,
        now=None
        ):
    session = get_db_session(request, 'famiport')
    try:
        internal.make_suborder_by_order_no(
            request,
            session,
            order_no,
            type_,
            reason=reason,
            cancel_reason_code=cancel_reason_code,
            cancel_reason_text=cancel_reason_text,
            client_code=client_code,
            now=now
        )
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def update_famiport_order_by_order_no(
        request,
        client_code,
        order_no=Unspecified,
        famiport_order_identifier=Unspecified,
        type_=Unspecified,
        event_code_1=Unspecified,
        event_code_2=Unspecified,
        performance_code=Unspecified,
        sales_segment_code=Unspecified,
        customer_name=Unspecified,
        customer_phone_number=Unspecified,
        customer_address_1=Unspecified,
        customer_address_2=Unspecified,
        total_amount=Unspecified,
        system_fee=Unspecified,
        ticketing_fee=Unspecified,
        ticket_payment=Unspecified,
        tickets=Unspecified,
        payment_start_at=Unspecified,
        payment_due_at=Unspecified,
        ticketing_start_at=Unspecified,
        ticketing_end_at=Unspecified,
        payment_sheet_text=Unspecified,
        require_ticketing_fee_on_ticketing=Unspecified
        ):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        def _u(v):
            return v if v != Unspecified else internal.Unspecified
        internal.update_famiport_order_by_order_no(
            session,
            client_code=_u(client_code),
            order_no=_u(order_no),
            famiport_order_identifier=_u(famiport_order_identifier),
            type_=_u(type_),
            event_code_1=_u(event_code_1),
            event_code_2=_u(event_code_2),
            performance_code=_u(performance_code),
            sales_segment_code=_u(sales_segment_code),
            customer_name=_u(customer_name),
            customer_phone_number=_u(customer_phone_number),
            customer_address_1=_u(customer_address_1),
            customer_address_2=_u(customer_address_2),
            total_amount=_u(total_amount),
            system_fee=_u(system_fee),
            ticketing_fee=_u(ticketing_fee),
            ticket_payment=_u(ticket_payment),
            tickets=_u(tickets),
            payment_start_at=_u(payment_start_at),
            payment_due_at=_u(payment_due_at),
            ticketing_start_at=_u(ticketing_start_at),
            ticketing_end_at=_u(ticketing_end_at),
            payment_sheet_text=_u(payment_sheet_text),
            require_ticketing_fee_on_ticketing=_u(require_ticketing_fee_on_ticketing)
            )
        session.commit()
    except (
            FamiportPaymentDateNoneError,
            FamiPortTicketingDateNoneError,
            FamiPortAlreadyPaidError
    ):
        raise
    except Exception:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_or_create_refund(
        request,
        client_code,
        send_back_due_at,
        start_at,
        end_at,
        userside_id=None,
        refund_id=None
        ):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_refund, new = internal.get_or_create_refund(
            session,
            client_code=client_code,
            send_back_due_at=send_back_due_at,
            start_at=start_at,
            end_at=end_at,
            userside_id=userside_id,
            refund_id=refund_id
            )
        session.commit()
        return dict(
            refund_id=famiport_refund.id,
            new=new
            )
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error', client_code)


@user_api
def refund_order_by_order_no(
        request,
        client_code,
        refund_id,
        per_ticket_fee,
        per_order_fee,
        refund_total_amount,
        order_no=None,
        famiport_order_identifier=None
        ):
    sys.exc_clear()
    try:
        internal.refund_order_by_order_no(
            request,
            client_code=client_code,
            refund_id=refund_id,
            order_no=order_no,
            famiport_order_identifier=famiport_order_identifier,
            per_ticket_fee=per_ticket_fee,
            per_order_fee=per_order_fee,
            refund_total_amount=refund_total_amount
            )
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')


@user_api
def get_genre_1_list(request):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        return session.query(FamiPortGenre1.code, FamiPortGenre1.name).all()
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_genre_2_list(request):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        return session.query(FamiPortGenre2.genre_1_code, FamiPortGenre2.code, FamiPortGenre2.name).all()
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def invalidate_famiport_event(request, userside_id, now=None):
    try:
        if now is None:
            now = datetime.now()
        session = get_db_session(request, 'famiport')

        internal.invalidate_famiport_event(session, userside_id, now)
        session.commit()
    except NoResultFound:
        raise FamiPortAPINotFoundError('no such famiport_event for userside_id: {}'.userside_id)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')
