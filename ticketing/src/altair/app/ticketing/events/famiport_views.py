# encoding: utf-8
import logging
from markupsafe import Markup
from pyramid.view import view_defaults, view_config, render_view_to_response
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
from sqlalchemy.sql import func as sqlf
from altair.sqlahelper import get_db_session
from altair.viewhelpers.datetime_ import create_date_time_formatter
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Event, FamiPortTenant
from altair.app.ticketing.famiport.models import FamiPortPrefecture, FamiPortPerformanceType, FamiPortSalesChannel
from altair.app.ticketing.famiport.userside_models import AltairFamiPortVenue, AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortReflectionStatus, AltairFamiPortSalesSegmentPair
from altair.app.ticketing.famiport.userside_api import build_famiport_performance_groups, submit_to_downstream

from .famiport_forms import AltairFamiPortPerformanceGroupForm, AltairFamiPortPerformanceForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class FamiPortView(BaseView):
    @property
    def session(self):
        return DBSession

    @property
    def slave_session(self):
        return get_db_session(self.request, 'slave')

    def status_label(self, status):
        u"""AltairFamiPortReflectionStatusに応じた表示用ラベル(html)を返す
        """
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

    def not_reflected_label(self, altair_famiport_obj):
        u"""AltairFamiPortPerformanceGroup, AltairFamiPortPerformance, AltairFamiPortSalesSegmentPair
        がFM側へ連携済みかどうかを表すラベルを返す
        """
        if altair_famiport_obj.last_reflected_at is not None:
            return u""
        label = u"未"
        class_ = u"label-important"
        return Markup(u'<span class="label %(class_)s">%(label)s</span>' % dict(class_=class_, label=label))


    def sales_channel_label(self, sales_channel):
        if sales_channel == FamiPortSalesChannel.FamiPortOnly.value:
            label = u'FP'
        elif sales_channel == FamiPortSalesChannel.WebOnly.value:
            label = u'Web販売'
        elif sales_channel == FamiPortSalesChannel.FamiPortAndWeb.value:
            label = u'FP+Web販売'
        return Markup(u'<span class="label">%s</span>' % label)

    def performance_type_label(self, status):
        if status == FamiPortPerformanceType.Normal.value:
            label = u'標準'
        elif status == AltairFamiPortReflectionStatus.AwaitingReflection.value:
            label = u'期間内有効'
        else:
            label = u'???'
        return label

    def last_reflected_at_label(self, famiport_performance_group):
        if famiport_performance_group.last_reflected_at is None:
            return u'-'
        else:
            return famiport_performance_group.last_reflected_at


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
        # 連携データの作成
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
            c, c_awaiting = self.session.query(
                    sqlf.count(),
                    sqlf.sum(AltairFamiPortPerformanceGroup.status == AltairFamiPortReflectionStatus.AwaitingReflection.value)
                    ) \
                .filter(AltairFamiPortPerformanceGroup.id.in_(altair_famiport_performance_group_ids)) \
                .one()
            if c_awaiting > 0:
                return dict(message=u'%d / %d件が「更新待ち」にセットされています。これらも含め強制的に「編集中」に戻してもよろしいですか?' % (c_awaiting, c))
            elif c > 0:
                return dict(message=u'%d件が「編集中」にセットされます。よろしいですか?' % c, count=c)
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


    @view_config(request_method='POST', route_name='events.famiport.performance_groups.action', name='submit_to_downstream')
    def submit_to_downstream(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        submit_to_downstream(self.request, event.id)
        self.request.session.flash(u'Famiポートに送信しました')
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

    @view_config(route_name='events.famiport.performance_groups.item.edit', renderer='events/famiport/performance_groups/edit.html', request_method='GET')
    def edit_performance_group(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        altair_famiport_performance_group_id = self.request.matchdict['altair_famiport_performance_group_id']
        altair_famiport_performance_group = self.slave_session.query(AltairFamiPortPerformanceGroup).filter_by(organization_id=self.context.organization.id, event_id=event.id, id=altair_famiport_performance_group_id).one()
        form = AltairFamiPortPerformanceGroupForm(
            context=self.context,
            _data=dict(
                name_1=altair_famiport_performance_group.name_1,
                name_2=altair_famiport_performance_group.name_2,
                sales_channel=altair_famiport_performance_group.sales_channel,
                genre_code=altair_famiport_performance_group.genre_1_code + \
                    (u'-%s' % altair_famiport_performance_group.genre_2_code
                     if altair_famiport_performance_group.genre_2_code
                     else u''),
                keywords=altair_famiport_performance_group.keywords,
                search_code=altair_famiport_performance_group.search_code
                )
            )
        return dict(
            event=event,
            form=form
            )

    @view_config(route_name='events.famiport.performance_groups.item.edit', renderer='events/famiport/performance_groups/edit.html', request_method='POST')
    def edit_performance_group_post(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        altair_famiport_performance_group_id = self.request.matchdict['altair_famiport_performance_group_id']
        altair_famiport_performance_group = self.session.query(AltairFamiPortPerformanceGroup).filter_by(organization_id=self.context.organization.id, event_id=event.id, id=altair_famiport_performance_group_id).one()
        form = AltairFamiPortPerformanceGroupForm(
            formdata=self.request.POST,
            context=self.context
            )
        if not form.validate():
            return dict(
                event=event,
                form=form
                )
        genre_1_code, _, genre_2_code = form.genre_code.data.partition(u'-')
        if genre_2_code == u'':
            genre_2_code = None
        altair_famiport_performance_group.name_1 = form.name_1.data
        altair_famiport_performance_group.name_2 = form.name_2.data
        altair_famiport_performance_group.genre_1_code = genre_1_code
        altair_famiport_performance_group.genre_2_code = genre_2_code
        altair_famiport_performance_group.keywords = form.keywords.data
        altair_famiport_performance_group.search_code = form.search_code.data
        return HTTPFound(location=self.request.route_path('events.famiport.performance_groups.item.show', event_id=event_id, altair_famiport_performance_group_id=altair_famiport_performance_group_id))

    @view_config(route_name='events.famiport.performances.item.show', renderer='events/famiport/performances/show.html')
    def show_performance(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        altair_famiport_performance_group_id = self.request.matchdict['altair_famiport_performance_group_id']
        altair_famiport_performance_id = self.request.matchdict['altair_famiport_performance_id']
        altair_famiport_performance = self.slave_session \
            .query(AltairFamiPortPerformance) \
            .join(AltairFamiPortPerformance.altair_famiport_performance_group) \
            .filter(
                AltairFamiPortPerformanceGroup.organization_id == self.context.organization.id,
                AltairFamiPortPerformanceGroup.event_id == event.id,
                AltairFamiPortPerformance.altair_famiport_performance_group_id == altair_famiport_performance_group_id,
                AltairFamiPortPerformance.id == altair_famiport_performance_id
                ).one()
        return dict(
            event=event,
            altair_famiport_performance=altair_famiport_performance
            )

    @view_config(route_name='events.famiport.performances.item.edit', renderer='events/famiport/performances/edit.html', request_method='GET')
    def edit_performance(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        altair_famiport_performance_group_id = self.request.matchdict['altair_famiport_performance_group_id']
        altair_famiport_performance_id = self.request.matchdict['altair_famiport_performance_id']
        altair_famiport_performance = self.slave_session \
            .query(AltairFamiPortPerformance) \
            .join(AltairFamiPortPerformance.altair_famiport_performance_group) \
            .filter(
                AltairFamiPortPerformanceGroup.organization_id == self.context.organization.id,
                AltairFamiPortPerformanceGroup.event_id == event.id,
                AltairFamiPortPerformance.altair_famiport_performance_group_id == altair_famiport_performance_group_id,
                AltairFamiPortPerformance.id == altair_famiport_performance_id
                ).one()
        form = AltairFamiPortPerformanceForm(
            context=self.context,
            _data=dict(
                type=altair_famiport_performance.type,
                name=altair_famiport_performance.name,
                searchable=altair_famiport_performance.searchable,
                start_at=altair_famiport_performance.start_at,
                ticket_name=altair_famiport_performance.ticket_name
                )
            )
        return dict(
            event=event,
            altair_famiport_performance=altair_famiport_performance,
            form=form
            )

    @view_config(route_name='events.famiport.performances.item.edit', renderer='events/famiport/performances/edit.html', request_method='POST')
    def edit_performance_post(self):
        event_id = self.request.matchdict['event_id']
        event = self.slave_session.query(Event).filter_by(organization_id=self.context.organization.id, id=event_id).one()
        altair_famiport_performance_group_id = self.request.matchdict['altair_famiport_performance_group_id']
        altair_famiport_performance_id = self.request.matchdict['altair_famiport_performance_id']
        altair_famiport_performance = self.session \
            .query(AltairFamiPortPerformance) \
            .join(AltairFamiPortPerformance.altair_famiport_performance_group) \
            .filter(
                AltairFamiPortPerformanceGroup.organization_id == self.context.organization.id,
                AltairFamiPortPerformanceGroup.event_id == event.id,
                AltairFamiPortPerformance.altair_famiport_performance_group_id == altair_famiport_performance_group_id,
                AltairFamiPortPerformance.id == altair_famiport_performance_id
                ).one()
        form = AltairFamiPortPerformanceForm(
            formdata=self.request.POST,
            context=self.context
            )
        if not form.validate():
            return dict(
                event=event,
                altair_famiport_performance=altair_famiport_performance,
                form=form
                )
        altair_famiport_performance.type = form.type.data
        altair_famiport_performance.name = form.name.data
        altair_famiport_performance.searchable = form.searchable.data
        altair_famiport_performance.start_at = form.start_at.data
        altair_famiport_performance.ticket_name = form.ticket_name.data
        return HTTPFound(location=self.request.route_path('events.famiport.performances.item.show', event_id=event_id, altair_famiport_performance_id=altair_famiport_performance_id, altair_famiport_performance_group_id=altair_famiport_performance.altair_famiport_performance_group_id))

    @view_config(route_name='events.famiport.performances.item.delete', renderer='events/famiport/performance_groups/show.html', request_method='POST')
    def delete_performance_post(self):
        altair_famiport_performance_id = self.request.matchdict['altair_famiport_performance_id']
        altair_famiport_performance = self.session.query(AltairFamiPortPerformance)\
                                                  .filter(AltairFamiPortPerformance.id==altair_famiport_performance_id).one()
        try:
            altair_famiport_performance.delete()
            self.request.session.flash(u'FM公演を削除しました')
        except Exception, exception:
            self.request.session.flash(exception.message)

        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
