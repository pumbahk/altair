# encoding: utf-8
from datetime import timedelta, datetime
from sqlalchemy.sql import func as sqlf
from altair.app.ticketing.famiport.exc import FamiPortVenueCreateError, FamiPortAPIError
from altair.app.ticketing.famiport.userside_models import (
    AltairFamiPortVenue,
    AltairFamiPortVenue_Site,
    AltairFamiPortPerformanceGroup,
    AltairFamiPortPerformance,
    AltairFamiPortReflectionStatus,
    AltairFamiPortSalesSegmentPair
    )
from altair.app.ticketing.famiport.models import FamiPortPerformanceType, FamiPortSalesChannel, FamiPortPrefecture
from altair.app.ticketing.core.models import FamiPortTenant
from altair.app.ticketing.famiport.api import resolve_famiport_prefecture_by_name, create_or_get_famiport_venue
from .utils import (
    convert_famiport_kogyo_name_style,
    validate_convert_famiport_kogyo_name_style,
    )

def next_event_code(session, event):
    """FamiPortEvent.codeの元になるデータを生成"""
    code_1, code_2 = session.query(AltairFamiPortPerformanceGroup.code_1, sqlf.max(AltairFamiPortPerformanceGroup.code_2)) \
        .with_lockmode('update') \
        .filter(AltairFamiPortPerformanceGroup.organization_id == event.organization_id) \
        .filter(AltairFamiPortPerformanceGroup.event_id == event.id) \
        .one()
    if code_1 is not None:
        code_2 = u'%04d' % (int(code_2) + 1)
        return code_1, code_2

    code_1, = session.query(sqlf.max(AltairFamiPortPerformanceGroup.code_1)) \
        .filter(AltairFamiPortPerformanceGroup.organization_id == event.organization_id) \
        .with_lockmode('update') \
        .one()
    if code_1 is None:
        code_1 = u'000001'
    else:
        code_1 = u'%06d' % (int(code_1) + 1)
    return code_1, u'0001'


def next_performance_code(session, altair_famiport_performance_group_id):
    """FamiPortPerformance.codeの元になるデータを生成"""
    code, = session.query(sqlf.max(AltairFamiPortPerformance.code)) \
        .filter(AltairFamiPortPerformance.altair_famiport_performance_group_id == altair_famiport_performance_group_id) \
        .with_lockmode('update') \
        .one()
    if code is not None:
        code = u'%03d' % (int(code) + 1)
        return code
    else:
        return u'001'


def next_sales_segment_code(session, altair_famiport_performance_id):
    """FamiPortSalesSegment.codeの元になるデータを生成"""
    code, = session.query(sqlf.max(AltairFamiPortSalesSegmentPair.code)) \
        .filter(AltairFamiPortSalesSegmentPair.altair_famiport_performance_id == altair_famiport_performance_id) \
        .with_lockmode('update') \
        .one()
    if code is not None:
        code = u'%03d' % (int(code) + 1)
        return code
    else:
        return u'001'


def lookup_altair_famiport_venue(session, performance):
    """公演情報から既存のAltairFamiPortVenueがあるか探す
    存在しない場合はNotFoundException例外を上げる
    """
    return session.query(AltairFamiPortVenue)\
        .filter(AltairFamiPortVenue.organization_id == performance.event.organization_id)\
        .filter(AltairFamiPortVenue.siteprofile_id == performance.venue.site.siteprofile_id)\
        .filter(AltairFamiPortVenue.venue_name == performance.venue.name)\
        .filter(AltairFamiPortVenue.deleted_at == None)\
        .one()


def lookup_altair_famiport_performance_group(session, performance, altair_famiport_venue):
    """公演情報から既存のAltairFamiPortPerformanceGroupがあるか探す
    存在しない場合はNotFoundException例外を上げる
    """
    return session.query(AltairFamiPortPerformanceGroup)\
        .filter(AltairFamiPortPerformanceGroup.event_id == performance.event_id)\
        .filter(AltairFamiPortPerformanceGroup.altair_famiport_venue_id == altair_famiport_venue.id)\
        .one()


def lookup_altair_famiport_performance(session, performance):
    """公演情報から既存のAltairFamiPortPerformanceがあるか探す
    存在しない場合はNotFoundException例外を上げる
    """
    return session.query(AltairFamiPortPerformance)\
        .filter(AltairFamiPortPerformance.performance_id==performance.id)\
        .filter(AltairFamiPortPerformance.deleted_at == None)\
        .one()


def lookup_altair_famiport_sales_segment_pair(session, sales_segment):
    """販売区分情報から既存のAltairFamiPortSalesSegmentPairがあるか探す
    存在しない場合はNotFoundException例外を上げる
    """
    ss_pair = None
    if sales_segment.seat_choice:
        ss_pair = session.query(AltairFamiPortSalesSegmentPair)\
            .filter(AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == sales_segment.id)\
            .filter(AltairFamiPortSalesSegmentPair.deleted_at == None)\
            .one()
    else:
        ss_pair = session.query(AltairFamiPortSalesSegmentPair)\
            .filter(AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == sales_segment.id)\
            .filter(AltairFamiPortSalesSegmentPair.deleted_at == None)\
            .one()
    return ss_pair


def select_performance_type_and_ticket_name(datetime_formatter, performance):
    """FamiPortPerformanceのタイプと券名を返す
    タイプ：１日券、期間券
    １日券名：なし
    期間券名：{終了日}まで有効
    """
    if performance.end_on is None or performance.end_on - performance.start_on < timedelta(days=1):
        type = FamiPortPerformanceType.Normal.value
        ticket_name = None
    else:
        type = FamiPortPerformanceType.Spanned.value
        ticket_name = u'(%sまで有効)' % datetime_formatter.format_date(performance.end_on, with_weekday=True)
    return type, ticket_name


def update_altair_famiport_performance_if_needed(request, session, altair_famiport_performance, performance, altair_famiport_performance_group, datetime_formatter, now=None):
    """AltairFamiPortPerformanceを更新する"""
    if now is None:
        now = datetime.now()
    updated = False
    if altair_famiport_performance.altair_famiport_performance_group_id != altair_famiport_performance_group.id:
        code_ = next_performance_code(session, altair_famiport_performance_group.id)
        altair_famiport_performance.altair_famiport_performance_group_id = altair_famiport_performance_group.id
        altair_famiport_performance.code = code_
        updated = True

    if altair_famiport_performance.start_at != performance.start_on:
        altair_famiport_performance.start_at = performance.start_on
        request.session.flash(u'公演「%s」(id=%ld, 日時=%s) の公演日を更新しました' % (performance.name, performance.id, str(performance.start_on)))
        updated = True

    type_, ticket_name_ = select_performance_type_and_ticket_name(datetime_formatter, performance)
    if altair_famiport_performance.type != type_:
        altair_famiport_performance.type = type_
        updated = True

    if altair_famiport_performance.ticket_name != ticket_name_:
        altair_famiport_performance.ticket_name = ticket_name_
        updated = True

    if updated:
        altair_famiport_performance.updated_at = now
        request.session.flash(u'公演「%s」(id=%ld) の連携値を更新しました' % (performance.name, performance.id))

    altair_famiport_performance.status = AltairFamiPortReflectionStatus.AwaitingReflection.value
    return altair_famiport_performance


def update_altair_famiport_sales_segment_pair_if_needed(request, session, afm_sales_segment_pair, unsele_ss, sele_ss, now=None):
    """AltairFamiPortSalesSegmentPairを更新する
    FIXME: start_at, end_atは更新が必要かfamiport側に問い合わせないと分からないので
    更新が必要ない可能性があっても反映待ちステータスにする
    """
    if now is None:
        now = datetime.now()

    origin_sales_segment = unsele_ss or sele_ss
    if afm_sales_segment_pair.name != origin_sales_segment.sales_segment_group.name:
        afm_sales_segment_pair.name = origin_sales_segment.sales_segment_group.name

    afm_sales_segment_pair.status = AltairFamiPortReflectionStatus.AwaitingReflection.value
    afm_sales_segment_pair.updated_at = now
    request.session.flash(u'販売区分「%s」(id=%d) の連携値を更新しました' % (
        origin_sales_segment.sales_segment_group.name,
        origin_sales_segment.id
        ))


def sync_altair_famiport_venue(request, altair_famiport_venue, performance, client_code):
    """（famiportDB側に）FamiPortVenueを作成する"""
    prefecture = resolve_famiport_prefecture_by_name(request, performance.venue.site.siteprofile.prefecture.strip())
    try:
        famiport_venue_dict = create_or_get_famiport_venue(
            request,
            client_code=client_code,
            userside_id=altair_famiport_venue.id,
            name=altair_famiport_venue.venue_name,
            name_kana=u'',
            prefecture=prefecture,
            )
    except FamiPortAPIError as fmerror:
        logger.error('FamiPortVenueの作成に失敗しました:{}'.format(fmerror.message))
        raise FamiPortVenueCreateError('error occured during FamiPortVenue creation.')

    return famiport_venue_dict


def create_altair_famiport_venue(request, session, performance, name_kana=u''):
    """AltairFamiPortVenueを作成する"""
    altair_famiport_venue = AltairFamiPortVenue(
        organization_id=performance.event.organization_id,
        siteprofile_id=performance.venue.site.siteprofile_id,
        famiport_venue_id=None,
        venue_name=performance.venue.name,
        name=performance.venue.site.siteprofile.name,
        name_kana=name_kana,
        status=AltairFamiPortReflectionStatus.AwaitingReflection.value
    )
    session.add(altair_famiport_venue)
    tenant = session.query(FamiPortTenant).filter_by(organization_id=performance.event.organization_id).one()
    famiport_venue_dict = sync_altair_famiport_venue(request, altair_famiport_venue, performance, tenant.code)
    if famiport_venue_dict:
        # Update altair_famiport_venue.famiport_venue_id with created FamiPortVenue.id
        altair_famiport_venue.famiport_venue_id = int(famiport_venue_dict.get('venue_id'))
    session.flush()

    request.session.flash(u'新しく会場「%s」をFamiポート連携しました' % altair_famiport_venue.name)
    return altair_famiport_venue


def create_altair_famiport_performance_group(request, session, performance, altair_famiport_venue):
    """AltairFamiPortPerformanceGroupを作成する"""
    code_1, code_2 = next_event_code(session, performance.event)
    # 明確な要件がないので一旦公演名をグループ名にする
    name_1 = convert_famiport_kogyo_name_style(performance.name)
    if not validate_convert_famiport_kogyo_name_style(performance.name):
        request.session.flash(u'公演名が長すぎるか使用できない文字が含まれていたので変換しました: 公演「%s」(id=%ld)' % (performance.name, performance.id))

    altair_famiport_performance_group = AltairFamiPortPerformanceGroup(
        altair_famiport_venue=altair_famiport_venue,
        organization_id=performance.event.organization_id,
        event_id=performance.event_id,
        code_1=code_1,
        code_2=code_2,
        name_1=name_1,
        name_2=u'',
        sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
        direct_sales_data=dict(
            purchasable_prefectures=[FamiPortPrefecture.Nationwide.id],
            genre_1_code=u'1',
            genre_2_code=u'',
            keywords=[],
            search_code=u''
            ),
        status=AltairFamiPortReflectionStatus.AwaitingReflection.value
        )
    request.session.flash(u'新しく公演グループ「%s」を連携対象にしました' % name_1)
    return altair_famiport_performance_group


def create_altair_famiport_performance(request, session, performance, altair_famiport_performance_group, datetime_formatter):
    """AltairFamiPortPerformanceを作成する"""
    code_ = next_performance_code(session, altair_famiport_performance_group.id)
    name_ = convert_famiport_kogyo_name_style(performance.name)
    if not validate_convert_famiport_kogyo_name_style(performance.name):
        request.session.flash(u'公演名が長すぎるか使用できない文字が含まれていたので変換しました: 公演「%s」(id=%ld)' % (performance.name, performance.id))

    # １日券or期間券判定
    type_, ticket_name_ = select_performance_type_and_ticket_name(datetime_formatter, performance)

    altair_famiport_performance = AltairFamiPortPerformance(
            altair_famiport_performance_group=altair_famiport_performance_group,
            code=code_,
            name=name_,
            type=type_,
            ticket_name=ticket_name_,
            performance=performance,
            start_at=performance.start_on,
            status=AltairFamiPortReflectionStatus.AwaitingReflection.value
        )
    session.add(altair_famiport_performance)
    session.flush()
    request.session.flash(u'新しく公演「%s」(id=%ld)を連携対象にしました' % (performance.name, performance.id))
    return altair_famiport_performance


def validate_sales_segment_consistency(seat_unselectable_ss, seat_selectable_ss):
    # 数受けなのに指定フラグがたってる
    if seat_unselectable_ss and seat_unselectable_ss.seat_choice:
        return False
    # 指定なのに指定フラグがたっていない
    if seat_selectable_ss and not seat_selectable_ss.seat_choice:
        return False
    return True

def create_altair_famiport_sales_segment_pair(request, session, seat_unselectable_ss, seat_selectable_ss, altair_famiport_performance):
    """AltairFamiPortSalesSegmentPairを作成する"""
    base_sales_segment = seat_unselectable_ss or seat_selectable_ss
    name_ = base_sales_segment.sales_segment_group.name
    published_at = base_sales_segment.start_at
    altair_famiport_sales_segment_pair = AltairFamiPortSalesSegmentPair(
            altair_famiport_performance=altair_famiport_performance,
            code=next_sales_segment_code(session, altair_famiport_performance.id),
            name=name_,
            published_at=published_at,
            auth_required=False,
            auth_message=u'',
            seat_unselectable_sales_segment=seat_unselectable_ss,
            seat_selectable_sales_segment=seat_selectable_ss,
            status=AltairFamiPortReflectionStatus.AwaitingReflection.value
        )
    session.add(altair_famiport_performance)
    session.flush()
    request.session.flash(u'新しく販売区分「%s」(id=%d) を連携対象にしました' % (name_, base_sales_segment.id))
    return altair_famiport_sales_segment_pair