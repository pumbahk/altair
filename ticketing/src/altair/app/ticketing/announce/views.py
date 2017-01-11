# -*- coding: utf-8 -*-

import logging
import webhelpers.paginate as paginate
from collections import namedtuple, Iterable

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
from sqlalchemy import func, distinct

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, Product, SalesSegmentGroup, SalesSegment
from altair.app.ticketing.users.models import Announcement, AnnouncementTemplate, WordSubscription
from .forms import AnnouncementForm, ParameterForm

from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from datetime import datetime

from .utils import MacroEngine

logger = logging.getLogger(__name__)

Parameter = namedtuple('Parameter', ['key', 'value'])


@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Announce(BaseView):
    @view_config(route_name='announce.index', renderer='altair.app.ticketing:templates/announce/index.html')
    def index(self):
        mode = 'todo'
        if 'mode' in self.request.GET and self.request.GET['mode'] in ('todo', 'done'):
            mode = self.request.GET['mode']

        query = Announcement.query\
            .filter_by(organization_id=self.context.user.organization_id)\
            .order_by(Announcement.send_after)

        if mode == 'todo':
            query = query.filter_by(started_at=None)\
                .order_by(Announcement.send_after)
        else:
            query = query.filter(Announcement.started_at.isnot(None))\
                .order_by(Announcement.send_after.desc())

        announcements = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )

        return dict(announcements=announcements, mode=mode)

    @view_config(route_name='announce.list', renderer='altair.app.ticketing:templates/announce/list.html')
    def list(self):
        try:
            event_id = int(self.request.matchdict.get('event_id', 0))
        except ValueError as e:
            return HTTPNotFound('event id not found')

        event = Event.get(event_id, organization_id=self.context.user.organization_id)

        announcements = Announcement.query.filter_by(event_id=event.id)\
            .order_by(Announcement.send_after)\
            .all()

        templates = AnnouncementTemplate.query.filter_by(organization_id=self.context.user.organization_id)\
            .order_by(AnnouncementTemplate.sort).all()

        return dict(announcements=announcements, event=event, templates=templates)

    @view_config(route_name='announce.new', renderer='altair.app.ticketing:templates/announce/form.html')
    def create(self):
        try:
            event_id = int(self.request.matchdict.get('event_id', 0))
        except ValueError as e:
            return HTTPNotFound('event id not found')

        event = Event.get(event_id, organization_id=self.context.user.organization_id)

        if event is None:
            return HTTPNotFound('event is not found')

        f = AnnouncementForm(self.request.POST)

        if self.request.method == 'POST':
            if f.validate():
                # INSERTする
                announce = Announcement()
                announce.organization_id = self.context.user.organization_id
                announce.event_id = event.id

                f.update_obj(announce)

                announce.save()

                self.request.session.flash(u'告知メールを登録しました')
                return HTTPFound(location=route_path('announce.list', self.request, event_id=event.id))
        else:
            if 'template' in self.request.GET:
                template = AnnouncementTemplate.query\
                .filter_by(organization_id=self.context.user.organization_id, name=self.request.GET['template']).first()
                if template is not None:
                    # TODO: makoを使った方が日付フォーマットとかが楽だが、DB内のtemplateに対して適用するのは、セキュリティ上、抵抗がある
                    engine = MacroEngine()

                    session = get_db_session(self.request, name="slave")

                    ssg_query = session.query(SalesSegmentGroup, SalesSegment).filter(SalesSegmentGroup.event_id==event.id)\
                    .join(SalesSegment)

                    #product_exists = Product.query.with_entities(Product.sales_segment_id).subquery()
                    #ssg_query = ssg_query.filter(SalesSegment.id.in_(product_exists))

                    try:
                        ssg_id = int(self.request.params.get('salessegmentgroup_id', 0))
                        result = ssg_query.filter(SalesSegmentGroup.id==ssg_id).first()
                        logger.debug(result)
                    except Exception as e:
                        logger.warn(e)
                        result = None
                    if result is None:
                        result = min(ssg_query.all(), key=lambda x:x.SalesSegment.start_at)
                    if result:
                        ssg = result.SalesSegmentGroup
                    data = dict(
                        event=event,
                        sales_segment=dict(
                            name=ssg.name if ssg else None,
                            start_at=ssg.start_at if ssg else None)
                    )
                    f.subject.process_data(engine.build(template.subject, data))
                    #f.message.process_data(engine.build(template.message, data))
                    f.message.process_data(template.message)

                    # テンプレートからプレースホルダーを抽出する
                    for v in engine.fields(template.message):
                        f.parameters.append_entry(Parameter(v, engine._macro(v, data)))

            if 'send_after' in self.request.GET and 0 < len(self.request.GET['send_after']):
                f.send_after.process_data(datetime.strptime(self.request.GET['send_after'], '%Y-%m-%d %H:%M:%S'))

        return dict(
            id=None,
            event=event,
            announce=None,
            form=f,
        )

    @view_config(route_name='announce.edit', renderer='altair.app.ticketing:templates/announce/form.html')
    def edit(self):
        try:
            announce_id = int(self.request.matchdict.get('announce_id', 0))
        except ValueError as e:
            return HTTPNotFound('announce id not found')

        announce = Announcement.get(announce_id, organization_id=self.context.user.organization_id)
        if announce is None:
            return HTTPNotFound('announce is not found')

        f = AnnouncementForm(self.request.POST, obj=announce)

        if self.request.method == 'POST':
            # TODO: validation before delete
            if "delete" in self.request.POST and 0 < len(self.request.POST["delete"]):
                # TODO: need lock before delete
                announce.delete()
                self.request.session.flash(u'告知メールを削除しました')
                return HTTPFound(location=route_path('announce.list', self.request, event_id=announce.event.id))

            if f.validate():
                f.update_obj(announce)
                announce.save()

                self.request.session.flash(u'告知メールを更新しました')
                return HTTPFound(location=route_path('announce.list', self.request, event_id=announce.event.id))

        f.parameters.process(None, [ ])
        f.parameters.last_index = -1

        engine = MacroEngine()
        for v in engine.fields(announce.message):
            f.parameters.append_entry(Parameter(v, announce.parameters[v] if announce.parameters is not None and v in announce.parameters else ''))

        return dict(
            id=announce_id,
            event=announce.event,
            announce=announce,
            form=f,
        )

    @view_config(route_name='announce.count', request_method='POST', renderer='json')
    def count(self):
        session = get_db_session(self.request, name="slave")
        try:
            word_ids = [ int(x) for x in self.request.params.getall('word_ids[]') ]
            if 0 < len(word_ids):
                r = session.query(func.count(distinct(WordSubscription.user_id)).label('count'))\
                    .filter(WordSubscription.word_id.in_(word_ids)).first()
                return dict(count=r.count)
            else:
                return dict(count=0)
        except Exception as e:
            logger.warn(e)
            return dict()

    @view_config(route_name='announce.macro', request_method='POST', renderer='json')
    def render(self):
        """templateとdataを受け取ってmacro engineでrenderする"""
        req = self.request.json_body

        try:
            engine = MacroEngine()
            return dict(result=engine.build(req["template"], req["data"], cache_mode=True))

        except Exception as e:
            return dict(error=e.message)