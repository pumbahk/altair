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
from .exc import FamiPortAPIError, FamiPortAPINotFoundError
from .communication.api import (  # noqa
    get_response_builder,  # noqa B/W compatibility
    get_xmlResponse_generator,  # noqa B/W compatibility
    )
from . import internal_api as internal

logger = logging.getLogger(__name__)

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

def famiport_performance_dict(famiport_performance):
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

def famiport_event_dict(famiport_event):
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
    reserve_number = None
    exchange_number = None
    for famiport_receipt in famiport_order.famiport_receipts:
        if famiport_receipt.type in (FamiPortReceiptType.CashOnDelivery.value, FamiPortReceiptType.Payment.value):
            reserve_number = famiport_receipt.reserve_number
        elif famiport_receipt.type == FamiPortReceiptType.Ticketing.value:
            exchange_number = famiport_receipt.reserve_number
        else:
            raise AssertionError('?')
    if famiport_order.type == FamiPortOrderType.Ticketing.value:
        reserve_number = exchange_number
    elif famiport_order.type == FamiPortOrderType.CashOnDelivery.value:
        exchange_number = reserve_number

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
        reserve_number=reserve_number,
        exchange_number=exchange_number,
        famiport_tickets=[
            dict(
                type=famiport_ticket.type,
                barcode_number=famiport_ticket.barcode_number,
                template=famiport_ticket.template_code,
                data=famiport_ticket.data,
                subticket=famiport_ticket.is_subticket,
                logically_subticket=famiport_ticket.logically_subticket
                )
            for famiport_ticket in famiport_order.famiport_tickets
            ]
        )
    sales_segment_dict = famiport_sales_segment_to_dict(famiport_order.famiport_sales_segment)
    retval.update(
        event_code_1=sales_segment_dict['event_code_1'],
        event_code_2=sales_segment_dict['event_code_2'],
        performance_code=sales_segment_dict['performance_code'],
        sales_segment_code=sales_segment_dict['code']
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
        ticketing_end_at=None):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_sales_segment = internal.get_famiport_sales_segment_by_code(
            session,
            event_code_1=event_code_1,
            event_code_2=event_code_2,
            performance_code=performance_code,
            code=sales_segment_code
            )
        famiport_order = internal.create_famiport_order(
            session,
            client_code=client_code,
            type_=type_,
            famiport_sales_segment=famiport_sales_segment,
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
            ticketing_end_at=ticketing_end_at
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
def update_famiport_order_by_order_no(
        request,
        client_code,
        order_no=None,
        famiport_order_identifier=None,
        type_=None,
        event_code_1=None,
        event_code_2=None,
        performance_code=None,
        sales_segment_code=None,
        customer_name=None,
        customer_phone_number=None,
        customer_address_1=None,
        customer_address_2=None,
        total_amount=None,
        system_fee=None,
        ticketing_fee=None,
        ticket_payment=None,
        tickets=None,
        payment_start_at=None,
        payment_due_at=None,
        ticketing_start_at=None,
        ticketing_end_at=None):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        internal.update_famiport_order_by_order_no(
            session,
            client_code=client_code,
            order_no=order_no,
            famiport_order_identifier=famiport_order_identifier,
            type_=type_,
            event_code_1=event_code_1,
            event_code_2=event_code_2,
            performance_code=performance_code,
            sales_segment_code=sales_segment_code,
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
            ticketing_end_at=ticketing_end_at
            )
        session.commit()
    except:
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
        order_no=None,
        famiport_order_identifier=None,
        ):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')

        internal.refund_order_by_order_no(
            session,
            client_code=client_code,
            refund_id=refund_id,
            order_no=order_no,
            famiport_order_identifier=famiport_order_identifier,
            per_ticket_fee=per_ticket_fee,
            per_order_fee=per_order_fee
            )
        session.commit()
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


