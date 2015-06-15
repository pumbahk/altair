# encoding: utf-8
import logging
import itertools
from datetime import timedelta
import sqlalchemy as sa
from markupsafe import Markup
from sqlalchemy import sql
from sqlalchemy.sql import func as sqlf
from sqlalchemy.orm.exc import NoResultFound
from pyramid.view import view_defaults, view_config, render_view_to_response
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from altair.sqlahelper import get_db_session
from altair.viewhelpers.datetime_ import create_date_time_formatter
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Site, Venue, Event, Performance, SalesSegment, SalesSegment_PaymentDeliveryMethodPair, PaymentDeliveryMethodPair, FamiPortTenant, PaymentMethod, DeliveryMethod
from altair.app.ticketing.famiport.models import FamiPortPrefecture, FamiPortPerformanceType, FamiPortSalesChannel
from altair.app.ticketing.famiport.exc import FamiPortAPINotFoundError
from altair.app.ticketing.famiport.api import get_famiport_venue_by_userside_id, resolve_famiport_prefecture_by_name, create_or_update_famiport_venue
from altair.app.ticketing.famiport.userside_models import AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortReflectionStatus, AltairFamiPortSalesSegmentPair
from altair.app.ticketing.payments.plugins import FAMIPORT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID

logger = logging.getLogger(__name__)

def next_event_code(session, event):
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
    code, = session.query(sqlf.max(AltairFamiPortSalesSegmentPair.code)) \
        .filter(AltairFamiPortSalesSegmentPair.altair_famiport_performance_id == altair_famiport_performance_id) \
        .with_lockmode('update') \
        .one()
    if code is not None:
        code = u'%03d' % (int(code) + 1)
        return code
    else:
        return u'001'

def find_sales_segment_pairs(session, sales_segments):
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
        if a.public:
            if i + 1 < len(sales_segments):
                b = sales_segments[i + 1]
                if b.public and \
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

def build_famiport_performance_groups(request, session, datetime_formatter, tenant, event_id):
    event = session.query(Event).filter_by(id=event_id).one()
    assert tenant.organization_id == event.organization_id
    logs = []
    client_code = tenant.code
    altair_famiport_performance_groups = session.query(AltairFamiPortPerformanceGroup).filter(AltairFamiPortPerformanceGroup.event_id == event.id)
    performances_by_venue = {} 
    altair_famiport_venues_just_added = set()
    altair_famiport_performances_just_added = set()
    for performance in event.performances:
        altair_famiport_venue = None
        try:
            altair_famiport_venue = session.query(AltairFamiPortVenue).filter_by(organization_id=event.organization_id, site_id=performance.venue.site_id).one()
        except NoResultFound:
            pass
        logger.info('no correspoding AltairFamiPortVenue record for site_id=%ld' % performance.venue.site_id)
        if altair_famiport_venue is None:
            # まずはFamiPort側に対応するレコードがないか調べる
            famiport_venue_info = None
            try:
                famiport_venue_info = get_famiport_venue_by_userside_id(request, client_code, performance.venue.site_id)
            except FamiPortAPINotFoundError:
                pass
            if famiport_venue_info is not None:
                famiport_venue_id = famiport_venue_info['venue_id']
                prefecture = famiport_venue_info['prefecture']
            else:
                prefecture = resolve_famiport_prefecture_by_name(request, performance.venue.site.prefecture)
                result = create_or_update_famiport_venue(
                    request,
                    client_code=client_code,
                    id=None,
                    userside_id=performance.venue.site_id,
                    name=performance.venue.site.name,
                    name_kana=u'',
                    prefecture=prefecture,
                    update_existing=False
                    )
                famiport_venue_id = result['venue_id']
            altair_famiport_venue = AltairFamiPortVenue(
                organization_id=event.organization_id,
                site=performance.venue.site,
                famiport_venue_id=famiport_venue_id,
                name=performance.venue.site.name,
                name_kana=u'',
                status=AltairFamiPortReflectionStatus.Editing.value
                )
            session.add(altair_famiport_venue)
            session.flush()
            altair_famiport_venues_just_added.add(altair_famiport_venue.id)
            logs.append(u'会場「%s」はファミポート未連携のために自動的に連携対象としました' % performance.venue.site.name)
        else:
            if not altair_famiport_venue.id not in altair_famiport_venues_just_added:
                if altair_famiport_venue.status == AltairFamiPortReflectionStatus.AwaitingReflection.value:
                    logs.append(u'会場「%s」は、反映待ちとなっており自動更新できません' % performance.venue.site.name)
                elif altair_famiport_venue.status == AltairFamiPortReflectionStatus.Reflected.value:
                    logs.append(u'会場「%s」は、反映済となっており自動更新できません。一度編集状態に戻してください' % performance.venue.site.name)
                elif altair_famiport_venue.status == AltairFamiPortReflectionStatus.Editing.value:
                    logs.append(u'会場「%s」の、連携値を更新しました' % performance.venue.site.name)
                    prefecture = resolve_famiport_prefecture_by_name(request, performance.venue.site.prefecture)
                    altair_famiport_venue.name = performance.venue.site.name
                    result = create_or_update_famiport_venue(
                        request,
                        client_code=client_code,
                        id=famiport_venue_id,
                        userside_id=performance.venue.site_id,
                        name=performance.venue.site.name,
                        name_kana=u'',
                        prefecture=prefecture,
                        update_existing=True
                        )
                    if result['new']:
                        logs.append(u'会場「%s」が予期せず再連携されています。システム管理者に連絡してください' % performance.venue.site.name)

        performances_for_venue = performances_by_venue.get(altair_famiport_venue)
        if performances_for_venue is None:
            performances_by_venue[altair_famiport_venue] = performances_for_venue = []
        performances_for_venue.append(performance)

    for altair_famiport_venue, performances_for_venue in performances_by_venue.items():
        altair_famiport_performance_group = None
        try:
            altair_famiport_performance_group = session.query(AltairFamiPortPerformanceGroup) \
                .filter(AltairFamiPortPerformanceGroup.event_id == event.id) \
                .filter(AltairFamiPortPerformanceGroup.altair_famiport_venue_id == altair_famiport_venue.id) \
                .one()
        except NoResultFound:
            pass
        performances_by_venue = sorted(performances_for_venue, key=lambda performance: performance.start_on)
        if altair_famiport_performance_group is None:
            code_1, code_2 = next_event_code(session, event)
            if len(performances_for_venue) > 1:
                name_1 = u'%s など%d公演' % (performances_for_venue[0].name, len(performances_for_venue))
            else:
                name_1 = performances_for_venue[0].name
            logs.append(u'公演グループ「%s」を新たに連携設定しました' % name_1)
            altair_famiport_performance_group = AltairFamiPortPerformanceGroup(
                altair_famiport_venue=altair_famiport_venue,
                organization=event.organization,
                event=event,
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
                status=AltairFamiPortReflectionStatus.Editing.value
                )
            session.add(altair_famiport_performance_group)
            session.flush()

        if altair_famiport_performance_group.status == AltairFamiPortReflectionStatus.AwaitingReflection.value:
            logs.append(u'公演グループ「%s」(%s-%s) は、反映待ちとなっており自動更新できません' % (altair_famiport_performance_group.name_1, altair_famiport_performance_group.code_1, altair_famiport_performance_group.code_2))
        else:
            for performance in performances_for_venue:
                altair_famiport_performance = altair_famiport_performance_group.altair_famiport_performances.get(performance)
                if performance.end_on is None or performance.end_on - performance.start_on < timedelta(days=1):
                    type_ = FamiPortPerformanceType.Normal.value
                    ticket_name = None
                else:
                    type_ = FamiPortPerformanceType.Spanned.value
                    ticket_name = u'(%sまで有効)' % datetime_formatter.format_date(performance.end_on, with_weekday=True)

                if altair_famiport_performance is None:
                    logs.append(u'公演「%s」(id=%ld) を新たに連携設定しました' % (performance.name, performance.id))
                    code = next_performance_code(session, altair_famiport_performance_group.id)
                    altair_famiport_performance = AltairFamiPortPerformance(
                        altair_famiport_performance_group=altair_famiport_performance_group,
                        code=code,
                        name=performance.name,
                        type=type_,
                        ticket_name=ticket_name,
                        performance=performance,
                        start_at=performance.start_on,
                        status=AltairFamiPortReflectionStatus.Editing.value
                        )
                    session.add(altair_famiport_performance)
                    session.flush()
                    altair_famiport_performances_just_added.add(altair_famiport_performance.id)
                else:
                    if not altair_famiport_performance.id not in altair_famiport_performances_just_added:
                        if altair_famiport_performance.status == AltairFamiPortReflectionStatus.AwaitingReflection.value:
                            logs.append(u'公演「%s」(id=%ld) は、反映待ちとなっており自動更新できません' % (performance.name, performance.id))
                        elif altair_famiport_performance.status == AltairFamiPortReflectionStatus.Reflected.value:
                            logs.append(u'公演「%s」(id=%ld) は、反映済となっており自動更新できません。一度編集状態に戻してください。' % (performance.name, performance.id))
                        elif altair_famiport_performance.status == AltairFamiPortReflectionStatus.Editing.value:
                            logs.append(u'公演「%s」(id=%ld) の連携値を更新しました' % (performance.name, performance.id))
                            altair_famiport_performance.name = performance.name
                            altair_famiport_performance.type = type_
                            altair_famiport_performance.ticket_name = ticket_name
                            altair_famiport_performance.start_at = performance.start_on
                if altair_famiport_performance.status == AltairFamiPortReflectionStatus.Editing.value:
                    sales_segments = session.query(SalesSegment) \
                        .join(SalesSegment_PaymentDeliveryMethodPair, SalesSegment_PaymentDeliveryMethodPair.c.sales_segment_id == SalesSegment.id) \
                        .join(PaymentDeliveryMethodPair, SalesSegment_PaymentDeliveryMethodPair.c.payment_delivery_method_pair_id == PaymentDeliveryMethodPair.id) \
                        .join(PaymentDeliveryMethodPair.payment_method) \
                        .join(PaymentDeliveryMethodPair.delivery_method) \
                        .filter(
                            sql.and_(
                                sql.or_(PaymentMethod.payment_plugin_id == FAMIPORT_PAYMENT_PLUGIN_ID,
                                        DeliveryMethod.delivery_plugin_id == FAMIPORT_DELIVERY_PLUGIN_ID),
                                PaymentDeliveryMethodPair.public != 0
                                )
                            ) \
                        .filter(SalesSegment.performance_id == performance.id) \
                        .all()
                    sales_segment_pairs = list(find_sales_segment_pairs(session, sales_segments))
                    if len(sales_segment_pairs) > 0:
                        for seat_unselectable_sales_segment, seat_selectable_sales_segment in sales_segment_pairs:
                            pair_ids = []
                            non_none_sales_segments = []
                            if seat_unselectable_sales_segment is not None:
                                pair_ids.append(seat_unselectable_sales_segment.id)
                                non_none_sales_segments.append(seat_unselectable_sales_segment)
                            if seat_selectable_sales_segment is not None:
                                pair_ids.append(seat_selectable_sales_segment.id)
                                non_none_sales_segments.append(seat_selectable_sales_segment)
                            assert len(pair_ids) > 0
                            altair_famiport_sales_segment = None
                            inconsistent_sales_segment = None
                            try:
                                altair_famiport_sales_segment = session.query(AltairFamiPortSalesSegmentPair) \
                                    .filter(sql.or_(
                                        AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id.in_(pair_ids),
                                        AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id.in_(pair_ids)
                                        )) \
                                    .one()
                                if altair_famiport_sales_segment.seat_unselectable_sales_segment is not None and \
                                   altair_famiport_sales_segment.seat_unselectable_sales_segment.seat_choice:
                                    inconsistent_sales_segment = altair_famiport_sales_segment.seat_unselectable_sales_segment
                                elif altair_famiport_sales_segment.seat_selectable_sales_segment is not None and \
                                   not altair_famiport_sales_segment.seat_selectable_sales_segment.seat_choice:
                                    inconsistent_sales_segment = altair_famiport_sales_segment.seat_selectable_sales_segment
                            except NoResultFound:
                                pass
                            except MultipleResultsFound:
                                inconsistent_sales_segment = non_none_sales_segments[0]

                            if inconsistent_sales_segment is not None:
                                logs.append(u'販売区分「%s」(id=%d) は連携済みの値と一貫性のない状態になっており、正しく連携を行うことはできません' % (
                                    inconsistent_sales_segment.sales_segment_group.name,
                                    inconsistent_sales_segment.id
                                    ))
                            else:
                                if altair_famiport_sales_segment is None:
                                    for sales_segment in non_none_sales_segments:
                                        logs.append(u'販売区分「%s」(id=%d) を新たに連携設定しました' % (
                                            sales_segment.sales_segment_group.name,
                                            sales_segment.id
                                            ))
                                    code = next_sales_segment_code(session, altair_famiport_performance.id)
                                    altair_famiport_sales_segment = AltairFamiPortSalesSegmentPair(
                                        altair_famiport_performance=altair_famiport_performance,
                                        code=code,
                                        name=non_none_sales_segments[0].sales_segment_group.name,
                                        published_at=non_none_sales_segments[0].start_at,
                                        auth_required=False,
                                        auth_message=u'',
                                        seat_unselectable_sales_segment=seat_unselectable_sales_segment,
                                        seat_selectable_sales_segment=seat_selectable_sales_segment,
                                        status=AltairFamiPortReflectionStatus.Editing.value
                                        )
                                    session.add(altair_famiport_sales_segment)
                                else:
                                    if altair_famiport_sales_segment.status == AltairFamiPortReflectionStatus.Editing.value:
                                        for sales_segment in non_none_sales_segments:
                                            logs.append(u'販売区分「%s」(id=%d) の連携値を更新しました' % (
                                                sales_segment.sales_segment_group.name,
                                                sales_segment.id
                                                ))
                                        altair_famiport_sales_segment.seat_unselectable_sales_segment = seat_unselectable_sales_segment
                                        altair_famiport_sales_segment.seat_selectable_sales_segment = seat_selectable_sales_segment
                                    elif altair_famiport_sales_segment.status == AltairFamiPortReflectionStatus.AwaitingReflection.value:
                                        for sales_segment in non_none_sales_segments:
                                            logs.append(u'販売区分「%s」(id=%d) は連携待ちとなっており自動更新できません' % (
                                                sales_segment.sales_segment_group.name,
                                                sales_segment.id
                                                ))
                                    elif altair_famiport_sales_segment.status == AltairFamiPortReflectionStatus.Reflected.value:
                                        for sales_segment in non_none_sales_segments:
                                            logs.append(u'販売区分「%s」(id=%d) は、反映済となっており自動更新できません。一度編集状態に戻してください。' % (
                                                sales_segment.sales_segment_group.name,
                                                sales_segment.id
                                                ))
                    else: 
                        logs.append(u'公演「%s」(id=%ld) には、連携可能な販売区分がありません' % (performance.name, performance.id))

    return logs

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class FamiPortView(BaseView):
    @property
    def session(self):
        return DBSession

    @property
    def slave_session(self):
        return get_db_session(self.request, 'slave')

    def status_label(self, status):
        if status == AltairFamiPortReflectionStatus.Editing.value:
            label = u'編集中'
            class_ = u'label-important'
        elif status == AltairFamiPortReflectionStatus.AwaitingReflection.value:
            label = u'反映待ち'
            class_ = u'label-warning'
        elif status == AltairFamiPortReflectionStatus.Reflected.value:
            label = u'反映済'
            class_ = u'label-success'
        else:
            label = u'???'
            class_ = u'label-warning'

        return Markup(u'<span class="label %(class_)s">%(label)s</span>' % dict(class_=class_, label=label))

    def sales_channel_label(self, sales_channel):
        if sales_channel == FamiPortSalesChannel.FamiPortOnly.value:
            label = u'FP'
        elif sales_channel == FamiPortSalesChannel.WebOnly.value:
            label = u'Web販売'
        elif sales_channel == FamiPortSalesChannel.FamiPortAndWeb.value:
            label = u'FP+Web販売'
        return Markup(u'<span class="label">%s</span>' % label)

    @view_config(route_name='events.famiport.performance_groups.index', renderer=u'events/famiport/show.html')
    def show(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        altair_famiport_performance_groups = self.slave_session.query(AltairFamiPortPerformanceGroup).filter(AltairFamiPortPerformanceGroup.event_id == event_id)
        return dict(event=event, altair_famiport_performance_groups=altair_famiport_performance_groups)

    @view_config(request_method='POST', route_name='events.famiport.performance_groups.action', name='action_dispatch')
    def _action_dispatch(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        for k in self.request.POST.keys():
            if k.startswith('do_'):
                action = k[3:]
                from zope.interface import directlyProvides # XXX: render_view_to_response is virtually unusable with URL dispatch...
                directlyProvides(self.request, self.request.request_iface) # XXX: render_view_to_response is virtually unusable with URL dispatch...
                return render_view_to_response(self.context, self.request, action, True)
        return HTTPFound(self.request.route_path('events.famiport.performance_groups.index', event_id=event.id))

    @view_config(request_method='POST', route_name='events.famiport.performance_groups.action', name='auto_add')
    def auto_add(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        tenant = self.session.query(FamiPortTenant).filter_by(organization_id=event.organization.id).one()
        datetime_formatter = create_date_time_formatter(self.request)
        logs = build_famiport_performance_groups(self.request, self.session, datetime_formatter, tenant, event.id)
        if logs:
            for log in logs:
                self.request.session.flash(log)
        else:
            self.request.session.flash(u'更新対象はありませんでした')
        return HTTPFound(self.request.route_path('events.famiport.performance_groups.index', event_id=event.id))

    @view_config(request_method='POST', renderer='json', route_name='events.famiport.performance_groups.action', name='try_mark_checked', xhr=True)
    def try_mark_checked(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        status_enum = AltairFamiPortReflectionStatus[self.request.POST['reflection_status']]
        altair_famiport_performance_group_ids = [long(i) for i in self.request.POST.getall('altair_famiport_performance_group_id[]')]
        if status_enum == AltairFamiPortReflectionStatus.Editing:
            c = self.session.query(AltairFamiPortPerformanceGroup) \
                .filter(AltairFamiPortPerformanceGroup.id.in_(altair_famiport_performance_group_ids)) \
                .filter(AltairFamiPortPerformanceGroup.status == AltairFamiPortReflectionStatus.AwaitingReflection.value) \
                .count()
            if c > 0:
                return dict(message=u'%d件が「更新待ち」にセットされています。これらを強制的に「編集中」に戻してもよろしいですか?' % c, count=c)
        elif status_enum == AltairFamiPortReflectionStatus.AwaitingReflection: 
            c = self.session.query(AltairFamiPortPerformanceGroup) \
                .filter(AltairFamiPortPerformanceGroup.id.in_(altair_famiport_performance_group_ids)) \
                .filter(AltairFamiPortPerformanceGroup.status == AltairFamiPortReflectionStatus.Editing.value) \
                .count()
            if c > 0:
                return dict(message=u'%d件が「更新待ち」にセットされます。よろしいですか?' % c, count=c)
        return dict(message=u'更新対象はありません', count=0)

    @view_config(request_method='POST', route_name='events.famiport.performance_groups.action', name='mark_checked')
    def mark_checked(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        status_enum = AltairFamiPortReflectionStatus[self.request.POST['reflection_status']]
        altair_famiport_performance_group_ids = [long(i) for i in self.request.POST.getall('altair_famiport_performance_group_id[]')]
        if status_enum == AltairFamiPortReflectionStatus.AwaitingReflection:
            # 「更新済み」のものを「更新待ち」に変更できないようにする
            def modifier(q, entity):
                return q.filter(entity.status == AltairFamiPortReflectionStatus.Editing.value)
            status_text = u'反映待ち'
        elif status_enum == AltairFamiPortReflectionStatus.Editing:
            status_text = u'編集中'
            modifier = lambda q, entity: q
        else:
            self.request.session.flash(u'予期せぬエラーです')
            return HTTPFound(self.request.route_path('events.famiport.performance_groups.index', event_id=event.id))

        entity_q_list = [
            (
                AltairFamiPortPerformanceGroup,
                self.session.query(AltairFamiPortPerformanceGroup)
                ),
            (
                AltairFamiPortVenue,
                self.session.query(AltairFamiPortVenue) \
                    .join(AltairFamiPortVenue.altair_famiport_performance_groups),
                ),
            (
                AltairFamiPortPerformance,
                self.session.query(AltairFamiPortPerformance) \
                    .join(AltairFamiPortPerformance.altair_famiport_performance_group),
                ),
            (
                AltairFamiPortSalesSegmentPair,
                self.session.query(AltairFamiPortSalesSegmentPair) \
                    .join(AltairFamiPortSalesSegmentPair.altair_famiport_performance) \
                    .join(AltairFamiPortPerformance.altair_famiport_performance_group),
                ),
            ]

        for entity, q in entity_q_list:
            q = q.filter(AltairFamiPortPerformanceGroup.id.in_(altair_famiport_performance_group_ids))
            q = modifier(q, entity)
            for r in q:
                logger.info('%d => %d', r.status, status_enum.value)
                r.status = status_enum.value
        self.request.session.flash(u'状態を「%(status_text)s」に設定しました' % dict(status_text=status_text))
        return HTTPFound(self.request.route_path('events.famiport.performance_groups.index', event_id=event.id))

    @view_config(route_name='events.famiport.performance_groups.item.show', renderer='events/famiport/performance_groups/show.html')
    def show_performance_group(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        altair_famiport_performance_group_id = self.request.matchdict['altair_famiport_performance_group_id']
        altair_famiport_performance_group = self.slave_session.query(AltairFamiPortPerformanceGroup).filter_by(organization_id=self.context.organization.id, event_id=event.id, id=altair_famiport_performance_group_id).one()
        return dict(
            event=event,
            altair_famiport_performance_group=altair_famiport_performance_group
            )
