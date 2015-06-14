# -*- coding: utf-8 -*-
import sys
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
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

def user_api(fn):
    def _(*args, **kwargs):
        return fn(*args, **kwargs)
    functools.update_wrapper(_, fn)
    return _


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
    retval = dict(
        order_no=famiport_order.order_no,
        famiport_order_identifier=famiport_order.famiport_order_identifier,
        reserve_number=famiport_order.reserve_number,
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
        famiport_tickets=[
            dict(
                type=famiport_ticket.type,
                barcode_number=famiport_ticket.barcode_number,
                template=famiport_ticket.template_code,
                data=famiport_ticket.data
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
def get_famiport_order(request, order_no):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_order = internal.get_famiport_order(session, order_no)
        return famiport_order_to_dict(famiport_order)
    except NoResultFound:
        raise FamiPortAPIError('no such order: %s' % order_no)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_sales_segment_by_userside_id(request, userside_id):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_sales_segment = internal.get_famiport_sales_segment_by_userside_id(session, userside_id)
        return famiport_sales_segment_to_dict(famiport_sales_segment)
    except NoResultFound:
        raise FamiPortAPIError('no such sales_segment corresponds to userside_id: %d' % userside_id)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_performance_by_userside_id(request, userside_id):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_performance = internal.get_famiport_performance_by_userside_id(session, userside_id)
        return famiport_performance_to_dict(famiport_performance)
    except NoResultFound:
        raise FamiPortAPIError('no such performance corresponds to userside_id: %d' % userside_id)
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error')

@user_api
def get_famiport_event_by_userside_id(request, userside_id):
    sys.exc_clear()
    try:
        session = get_db_session(request, 'famiport')
        famiport_event = internal.get_famiport_event_by_userside_id(session, userside_id)
        return famiport_event_to_dict(famiport_event)
    except NoResultFound:
        raise FamiPortAPIError('no such event corresponds to userside_id: %d' % userside_id)
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
            raise FamiPortAPIError('internel error')
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
        update_existing=False):
    sys.exc_clear()
    new = False
    try:
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
        if genre_1_code is not None:
            try:
                genre_1 = session.query(FamiPortGenre1) \
                    .filter_by(code=genre_1_code) \
                    .one()
            except NoResultFound:
                raise FamiPortAPINotFoundError('no corresponding genre found for code=%s' % genre_1_code)

        genre_2 = None
        if genre_2_code is not None:
            try:
                genre_2 = session.query(FamiPortGenre2) \
                    .filter_by(code=genre_2_code) \
                    .one()
            except NoResultFound:
                raise FamiPortAPINotFoundError('no corresponding subgenre found for code=%s' % genre_2_code)

        event = None
        try:
            event = session.query(FamiPortEvent) \
                .filter(FamiPortEvent.client_code == client_code) \
                .filter(FamiPortEvent.code_1 == code_1) \
                .filter(FamiPortEvent.code_2 == code_2) \
                .one()
        except NoResultFound:
            pass
        sys.exc_clear()

        internal.validate_sales_channel(sales_channel)

        if not update_existing and event is not None:
            raise FamiPortAPIError(u'event already exists')

        if event is None:
            event = FamiPortEvent(
                client_code=client_code,
                code_1=code_1,
                code_2=code_2
                )
            session.add(event)
            new = True

        event.name_1 = name_1
        event.name_2 = name_2
        event.sales_channel = sales_channel
        event.venue_id = venue_id
        event.userside_id = userside_id
        event.genre_1_code = genre_1.code if genre_1 is not None else None
        event.genre_2_code = genre_2.code if genre_2 is not None else None
        event.keywords = keywords
        event.search_code = search_code
        event.need_reflection = True
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

        session.commit()
        return dict(
            new=new
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
        update_existing=False):
    sys.exc_clear()
    new = False
    try:
        session = get_db_session(request, 'famiport')
     
        internal.get_famiport_client(session, client_code)

        try:
            event = session.query(FamiPortEvent) \
                .filter(FamiPortEvent.client_code == client_code) \
                .filter(FamiPortEvent.code_1 == event_code_1) \
                .filter(FamiPortEvent.code_2 == event_code_2) \
                .one()
        except NoResultFound:
            raise FamiPortAPINotFoundError('no corresponding event found for client_code=%s, event_code_1=%s, event_code_2=%s' % (client_code, event_code_1, event_code_2))

        performance = None
        try:
            performance = session.query(FamiPortPerformance) \
                .filter(FamiPortPerformance.code == code) \
                .filter(FamiPortPerformance.famiport_event_id == event.id) \
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

        if not update_existing and performance is not None:
            raise FamiPortAPIError(u'performance already exists')

        if performance is None:
            performance = FamiPortPerformance(
                code=code,
                famiport_event_id=event.id
                )
            session.add(performance)
            new = True

        performance.code = code
        performance.name = name
        performance.type = type_
        performance.searchable = searchable
        performance.sales_channel = sales_channel
        performance.ticket_name = ticket_name
        performance.userside_id = userside_id
        performance.start_at = start_at
        performance.need_reflection = True

        session.commit()
        return dict(
            new=new
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
        update_existing=False):
    sys.exc_clear()
    new = False
    try:
        session = get_db_session(request, 'famiport')
     
        internal.get_famiport_client(session, client_code)

        try:
            performance = session.query(FamiPortPerformance) \
                .join(FamiPortPerformance.famiport_event) \
                .filter(FamiPortEvent.client_code == client_code) \
                .filter(FamiPortEvent.code_1 == event_code_1) \
                .filter(FamiPortEvent.code_2 == event_code_2) \
                .filter(FamiPortPerformance.code == performance_code) \
                .one()
        except NoResultFound:
            raise FamiPortAPINotFoundError('no corresponding performance found for client_code=%s, event_code_1=%s, event_code_2=%s, performance_code=%s' % (client_code, event_code_1, event_code_2, performance_code))

        sales_segment = None
        try:
            sales_segment = session.query(FamiPortSalesSegment) \
                .filter(FamiPortSalesSegment.code == code) \
                .filter(FamiPortSalesSegment.famiport_performance_id == performance.id) \
                .one()
        except NoResultFound:
            pass
        sys.exc_clear()

        internal.validate_sales_channel(sales_channel)

        if not update_existing and sales_segment is not None:
            raise FamiPortAPIError(u'sales_segment already exists')

        if sales_segment is None:
            sales_segment = FamiPortSalesSegment(
                code=code,
                famiport_performance_id=performance.id
                )
            session.add(sales_segment)
            new = True

        sales_segment.name = name
        sales_segment.sales_channel = sales_channel
        sales_segment.published_at = published_at
        sales_segment.start_at = start_at
        sales_segment.end_at = end_at
        sales_segment.auth_required = auth_required
        sales_segment.auth_message = auth_message
        sales_segment.seat_selection_start_at = seat_selection_start_at
        sales_segment.need_reflection = True

        session.commit()
        return dict(
            new=new
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
        internal.create_famiport_order(
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
    except FamiPortAPIError:
        raise
    except:
        logger.exception(u'internal error')
        raise FamiPortAPIError('internal error', client_code)

def do_order(*args, **kwds):
    return create_famiport_order(*args, **kwds)
