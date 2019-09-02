# encoding: utf-8
import logging
import itertools
from urllib import urlencode
from datetime import datetime, timedelta
import sqlalchemy as sa
import transaction
from markupsafe import Markup
from sqlalchemy import sql
from sqlalchemy.sql import func as sqlf
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.mq import get_publisher
from altair.app.ticketing.core.models import Site, Venue, Event, Performance, SalesSegment, SalesSegment_PaymentDeliveryMethodPair, PaymentDeliveryMethodPair, FamiPortTenant, PaymentMethod, DeliveryMethod
from altair.app.ticketing.famiport.models import FamiPortPrefecture, FamiPortPerformanceType, FamiPortSalesChannel
from altair.app.ticketing.famiport.exc import FamiPortAPIError, FamiPortAPINotFoundError, FamiPortVenueCreateError
from altair.app.ticketing.famiport.api import (
    get_famiport_venue_by_userside_id,
    get_famiport_venue_by_userside_id_or_name,
    get_famiport_venue_by_name,
    resolve_famiport_prefecture_by_name,
    create_or_get_famiport_venue,
    create_or_update_famiport_venue,
    create_or_update_famiport_event,
    create_or_update_famiport_performance,
    create_or_update_famiport_sales_segment,
    invalidate_famiport_event,
    move_orders_to_new_performance,
    move_orders_to_new_sales_segment,
)
from altair.app.ticketing.famiport.userside_models import (
    AltairFamiPortVenue,
    AltairFamiPortVenue_Site,
    AltairFamiPortPerformanceGroup,
    AltairFamiPortPerformance,
    AltairFamiPortReflectionStatus,
    AltairFamiPortSalesSegmentPair,
    )
from altair.app.ticketing.core.models import SalesSegment
from altair.app.ticketing.payments.plugins import FAMIPORT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID
from .utils import (
    convert_famiport_kogyo_name_style,
    validate_convert_famiport_kogyo_name_style,
    )
from . import userside_internal_api as internal

logger = logging.getLogger(__name__)

def get_altair_famiport_performance_by_performance(session, performance):
    return session.query(AltairFamiPortPerformance)\
        .filter(AltairFamiPortPerformance.performance_id==performance.id)\
        .first()

# Pair up given sales_segments as (seat_unselectable_sales_segment, seat_selectable_sales_segment)
# force_reflection=Trueのときは販売区分の公開区分に関わらず連携対象とする
def find_sales_segment_pairs(session, sales_segments, force_reflection=True):
    def _cmp(a, b):
        if a.start_at is None:
            return -1
        elif b.start_at is None:
            return 1
        else:
            return cmp(a.start_at, b.start_at)
    sales_segments = sorted(sales_segments, cmp=_cmp)
    i = 0
    while i < len(sales_segments):
        a = sales_segments[i]
        if (a.public or force_reflection):
            if i + 1 < len(sales_segments):
                b = sales_segments[i + 1]
                if (b.public or force_reflection) and \
                   a.sales_segment_group_id == b.sales_segment_group_id and \
                   a.end_at is not None and b.start_at is not None and a.end_at + timedelta(seconds=1) == b.start_at and \
                   not a.seat_choice and b.seat_choice:
                    yield (a, b)
                    i += 2
                    continue
            if a.seat_choice:
                yield None, a
            else:
                yield a, None
        i += 1


# TODO: 後で適当なところに移動させる
def filter_famiport_pdmp_sales_segments(sales_segments):
    fm_ss = []
    def has_famiport_pdmp(ss):
        for pdmp in ss.payment_delivery_method_pairs:
            if pdmp.use_famiport_plugin:
                return True
        return False

    for ss in sales_segments:
        if has_famiport_pdmp(ss):
            fm_ss.append(ss)

    return fm_ss


def create_famiport_reflection_data(request, session, event, datetime_formatter):
    """FM連携データ(中間データ)を作成,更新する
    中間データ： AltairFamiPortVenue, AltairFamiPortPerformanceGroup,
    AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
    """

    if filter_famiport_pdmp_sales_segments(event.sales_segment_groups):
        for performance in event.performances:
            # AltairFamiPortPerformance作成
            # Group取得のためにVenueを探すor作る
            try:
                afm_venue = internal.lookup_altair_famiport_venue(session, performance)
            except NoResultFound:
                try:
                    afm_venue = internal.create_altair_famiport_venue(request, session, performance)
                except FamiPortVenueCreateError:
                    continue
            # Group取得or作る
            try:
                afm_performance_group = internal.lookup_altair_famiport_performance_group(session, performance, afm_venue)
                # 連携時にGroupのstatusが反映待ちになってるか見るのでここでステータスを変えておく
                afm_performance_group.status = AltairFamiPortReflectionStatus.AwaitingReflection.value
            except NoResultFound:
                afm_performance_group = internal.create_altair_famiport_performance_group(request, session, performance, afm_venue)
            # AltairFamiPortPerformance取得or作る
            try:
                afm_performance = internal.lookup_altair_famiport_performance(session, performance)
                internal.update_altair_famiport_performance_if_needed(
                                                    request,
                                                    session,
                                                    afm_performance,
                                                    performance,
                                                    afm_performance_group,
                                                    datetime_formatter)
            except NoResultFound:
                afm_performance = internal.create_altair_famiport_performance(
                                                    request,
                                                    session,
                                                    performance,
                                                    afm_performance_group,
                                                    datetime_formatter)


            # AltairFamiPortSalesSegmentPair作成
            fm_sales_segments = filter_famiport_pdmp_sales_segments(performance.sales_segments)
            if afm_performance and fm_sales_segments:
                sales_segment_pairs = list(find_sales_segment_pairs(session, fm_sales_segments))

                for seat_unselectable_ss, seat_selectable_ss in sales_segment_pairs:

                    origin_sales_segment = seat_unselectable_ss or seat_selectable_ss

                    # 座席選択を切替られた場合を考慮
                    from datetime import datetime
                    from altair.app.ticketing.famiport.userside_models import AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair

                    query = session.query(AltairFamiPortSalesSegmentPair) \
                        .join(AltairFamiPortPerformance, AltairFamiPortPerformance.id == AltairFamiPortSalesSegmentPair.altair_famiport_performance_id) \
                        .filter(AltairFamiPortPerformance.performance_id == origin_sales_segment.performance.id)

                    if seat_unselectable_ss:
                        pair = query.filter(AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == origin_sales_segment.id).first()
                    else:
                        pair = query.filter(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == origin_sales_segment.id).first()

                    if pair:
                        pair.deleted_at = datetime.now()

                    if internal.validate_sales_segment_consistency(seat_unselectable_ss, seat_selectable_ss):
                        try:
                            afm_sales_segment_pair = internal.lookup_altair_famiport_sales_segment_pair(session, origin_sales_segment)
                            internal.update_altair_famiport_sales_segment_pair_if_needed(
                                                                                request,
                                                                                session,
                                                                                afm_sales_segment_pair,
                                                                                seat_unselectable_ss,
                                                                                seat_selectable_ss)
                        except NoResultFound:
                            internal.create_altair_famiport_sales_segment_pair(
                                                                        request,
                                                                        session,
                                                                        seat_unselectable_ss,
                                                                        seat_selectable_ss,
                                                                        afm_performance)
                        except MultipleResultsFound:
                            logger.error('Multiple AltairFamiPortSalesSegmentPair with same sales_segment(id: {}) was found.'.format(origin_sales_segment.id))
                            request.session.flash(u'販売区分「%s」(id=%d) においてデータ不整合が発生してます。システム管理者までお知らせ下さい。' % (
                                            origin_sales_segment.sales_segment_group.name,
                                            origin_sales_segment.id
                                            ))
                    else:
                        logger.error('Validating SalesSegment consistency failed. maybe mixing seat choice.(pID={},ssID={})'.format(performance.id,origin_sales_segment.id))
                        request.session.flash(u'販売区分「%s」(id=%d) においてデータ不整合が発生してます。システム管理者までお知らせ下さい。' % (
                                            origin_sales_segment.sales_segment_group.name,
                                            origin_sales_segment.id
                                            ))
            else:
                request.session.flash(u'公演「%s」(id=%ld) には、連携可能な販売区分がありません' % (performance.name, performance.id))

    else:
        request.session.flash(u'更新対象はありませんでした')


def submit_to_downstream(request, event_id):
    publisher = get_publisher(request, 'userside_famiport.submit_to_downstream')
    publisher.publish(
        body=urlencode(dict(event_id=event_id)),
        routing_key='userside_famiport.submit_to_downstream',
        properties=dict(content_type='application/x-www-form-urlencoded')
        )

def submit_to_downstream_sync(request, session, tenant, event):
    assert tenant.organization_id == event.organization_id
    from altair.app.ticketing.events.famiport_helpers import has_famiport_pdmp

    # Lock the FM reflection task with AltairFamiPortPerformanceGroup to avoid parallel execution from different worker process ref: TKT-1563
    altair_famiport_performance_groups = session.query(AltairFamiPortPerformanceGroup).with_lockmode("update").filter_by(event_id=event.id).all()

    for altair_famiport_performance_group in altair_famiport_performance_groups:

        from datetime import datetime
        now = datetime.now()

        # tkt3258 販売区分からファミマの販売区分がなくなった場合、中間データを削除する
        for altair_famiport_performance in altair_famiport_performance_group.altair_famiport_performances.values():

            for sales_segment_pair in altair_famiport_performance.altair_famiport_sales_segment_pairs:
                if sales_segment_pair.seat_unselectable_sales_segment_id:
                    origin_sales_segmet = SalesSegment.get(sales_segment_pair.seat_unselectable_sales_segment_id)
                else:
                    origin_sales_segmet = SalesSegment.get(sales_segment_pair.seat_selectable_sales_segment_id)

                # 販売区分削除時に、連携データ消すの処理が入る前に対応
                if not origin_sales_segmet:
                    sales_segment_pair.deleted_at = now

                if origin_sales_segmet and not has_famiport_pdmp(origin_sales_segmet):
                    sales_segment_pair.deleted_at = now

        try:
            get_famiport_venue_by_userside_id(
                request,
                tenant.code,
                altair_famiport_performance_group.altair_famiport_venue.id
                )
        except FamiPortAPINotFoundError:
            prefecture = resolve_famiport_prefecture_by_name(request, altair_famiport_performance_group.altair_famiport_venue.siteprofile.prefecture)
            result = create_or_update_famiport_venue(
                request,
                client_code=tenant.code,
                id=None,
                userside_id=altair_famiport_performance_group.altair_famiport_venue.id,
                name=altair_famiport_performance_group.altair_famiport_venue.venue_name,
                name_kana=u'',
                prefecture=prefecture,
                update_existing=True
                )
            altair_famiport_performance_group.altair_famiport_venue.famiport_venue_id = result['venue_id']
        # 連携済みのAltairFamiPortPerformanceGroup配下に公演がない場合はFamiPortEventを無効化する
        # TODO:FamiPortPerformance, FamiPortSalesSegmentも合わせて無効化した方が良い
        if not altair_famiport_performance_group.altair_famiport_performances:
            if altair_famiport_performance_group.last_reflected_at is not None:
                try:
                    invalidate_famiport_event(request, userside_id=altair_famiport_performance_group.id, now=now)
                    altair_famiport_performance_group.deleted_at = now
                except FamiPortAPINotFoundError:
                    logger.error(u'FamiPortEvent was not found for userside_id={}'.format(altair_famiport_performance_group.id))
                except FamiPortAPIError:
                    logger.error(u'error occured while invalidating AltairFamiPortPerformanceGroup(altair_famiport_performance_group_id: {})'.format(altair_famiport_performance_group.id))
            else:
                # famiportDBに未反映のデータはそのままdeleteする
                altair_famiport_performance_group.deleted_at = now
            continue
        if altair_famiport_performance_group.status != AltairFamiPortReflectionStatus.AwaitingReflection.value:
            logger.info('AltairFamiPortPerformanceGroup(id=%ld) is not marked AwaitingReflection; skipped' % altair_famiport_performance_group.id)
            continue
        result = create_or_update_famiport_event(
            request,
            tenant.code,
            altair_famiport_performance_group.id,
            code_1=altair_famiport_performance_group.code_1,
            code_2=altair_famiport_performance_group.code_2,
            name_1=altair_famiport_performance_group.name_1,
            name_2=altair_famiport_performance_group.name_2,
            sales_channel=altair_famiport_performance_group.sales_channel,
            venue_id=altair_famiport_performance_group.altair_famiport_venue.famiport_venue_id,
            purchasable_prefectures=altair_famiport_performance_group.direct_sales_data.get('purchasable_prefectures', None),
            start_at=altair_famiport_performance_group.start_at,
            end_at=altair_famiport_performance_group.end_at,
            genre_1_code=altair_famiport_performance_group.direct_sales_data.get('genre_1_code', u'1'),
            genre_2_code=altair_famiport_performance_group.direct_sales_data.get('genre_2_code', u''),
            keywords=altair_famiport_performance_group.direct_sales_data.get('keywords', []),
            search_code=altair_famiport_performance_group.direct_sales_data.get('search_code', u''),
            update_existing=True
            )
        altair_famiport_performance_group.status = AltairFamiPortReflectionStatus.Reflected.value
        altair_famiport_performance_group.last_reflected_at = now
        if result['new']:
            logger.info('AltairFamiPortPerformanceGroup(id=%ld) registered' % altair_famiport_performance_group.id)
        else:
            logger.info('AltairFamiPortPerformanceGroup(id=%ld) updated' % altair_famiport_performance_group.id)
        for altair_famiport_performance in altair_famiport_performance_group.altair_famiport_performances.values():
            if altair_famiport_performance.status != AltairFamiPortReflectionStatus.AwaitingReflection.value:
                logger.info('AltairFamiPortPerformance(id=%ld) is not marked AwaitingReflection; skipped' % altair_famiport_performance.id)
                continue
            result = create_or_update_famiport_performance(
                request,
                client_code=tenant.code,
                userside_id=altair_famiport_performance.id,
                event_code_1=altair_famiport_performance_group.code_1,
                event_code_2=altair_famiport_performance_group.code_2,
                code=altair_famiport_performance.code,
                name=altair_famiport_performance.name,
                type_=altair_famiport_performance.type,
                searchable=altair_famiport_performance.searchable,
                sales_channel=altair_famiport_performance_group.sales_channel,
                start_at=altair_famiport_performance.start_at,
                ticket_name=altair_famiport_performance.ticket_name,
                update_existing=True
                )
            altair_famiport_performance.status = AltairFamiPortReflectionStatus.Reflected.value
            altair_famiport_performance.last_reflected_at = now
            if result['new']:
                logger.info('AltairFamiPortPerformance(id=%ld) registered' % altair_famiport_performance.id)
            else:
                logger.info('AltairFamiPortPerformance(id=%ld) updated' % altair_famiport_performance.id)
            result = move_orders_to_new_performance(
                request,
                client_code=tenant.code,
                userside_id=altair_famiport_performance.id,
                event_code_1=altair_famiport_performance_group.code_1,
                event_code_2=altair_famiport_performance_group.code_2,
                code=altair_famiport_performance.code
            )
            logger.info('Moved %s orders to FamiPortPerformance related to AltairFamiPortPerformance(id=%s)',
                        result['number_of_moved_order'], altair_famiport_performance.id)

            for altair_famiport_sales_segment_pair in altair_famiport_performance.altair_famiport_sales_segment_pairs:
                if altair_famiport_sales_segment_pair.status != AltairFamiPortReflectionStatus.AwaitingReflection.value:
                    logger.info('AltairFamiPortSalesSegmentPair(id=%ld) is not marked AwaitingReflection; skipped' % altair_famiport_sales_segment_pair.id)
                    continue
                result = create_or_update_famiport_sales_segment(
                    request,
                    client_code=tenant.code,
                    userside_id=altair_famiport_sales_segment_pair.id,
                    event_code_1=altair_famiport_performance_group.code_1,
                    event_code_2=altair_famiport_performance_group.code_2,
                    performance_code=altair_famiport_performance.code,
                    code=altair_famiport_sales_segment_pair.code,
                    name=altair_famiport_sales_segment_pair.name,
                    sales_channel=altair_famiport_performance_group.sales_channel,
                    published_at=altair_famiport_sales_segment_pair.published_at,
                    start_at=altair_famiport_sales_segment_pair.start_at,
                    end_at=altair_famiport_sales_segment_pair.end_at,
                    auth_required=altair_famiport_sales_segment_pair.auth_required,
                    auth_message=altair_famiport_sales_segment_pair.auth_message,
                    seat_selection_start_at=altair_famiport_sales_segment_pair.seat_selection_start_at,
                    update_existing=True
                    )
                altair_famiport_sales_segment_pair.status = AltairFamiPortReflectionStatus.Reflected.value
                altair_famiport_sales_segment_pair.last_reflected_at = now
                if result['new']:
                    logger.info('AltairFamiPortSalesSegmentPair(id=%ld) registered' % altair_famiport_sales_segment_pair.id)
                else:
                    logger.info('AltairFamiPortSalesSegmentPair(id=%ld) updated' % altair_famiport_sales_segment_pair.id)

                result = move_orders_to_new_sales_segment(
                    request,
                    client_code=tenant.code,
                    userside_id=altair_famiport_sales_segment_pair.id,
                    event_code_1=altair_famiport_performance_group.code_1,
                    event_code_2=altair_famiport_performance_group.code_2,
                    performance_code=altair_famiport_performance.code,
                    code=altair_famiport_sales_segment_pair.code,
                    name=altair_famiport_sales_segment_pair.name,
                    start_at=altair_famiport_sales_segment_pair.start_at,
                    end_at=altair_famiport_sales_segment_pair.end_at,
                )
                logger.info('Moved %s orders to FamiPortSalesSegment related to AltairFamiPortSalesSegmentPair(id=%s)',
                            result['number_of_moved_order'], altair_famiport_sales_segment_pair.id)