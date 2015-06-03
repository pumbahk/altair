# -*- coding:utf-8 -*-
import logging
from datetime import datetime, timedelta
from webhelpers import paginate
from sqlalchemy import (
    #case_,
    sql,
    and_,
)
from sqlalchemy.orm import (
    joinedload,
)
from pyramid.view import view_config, view_defaults
from altair.app.ticketing.views import BaseView
from altair.sqlahelper import get_db_session
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import (
    SalesSegment,
    Event,
    EventSetting,
    Organization,
)
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex

from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    LotStatusEnum,
)

from .models import (
    LotEntrySearch,
)
from .forms import (
    SearchLotEntryForm,
)
from altair.app.ticketing.lots import helpers as h
from altair.app.ticketing.events.lots import helpers as eh

logger = logging.getLogger(__name__)


@view_defaults(route_name='altair.app.ticketing.lots_admin.index',
               decorator=with_bootstrap, permission='event_editor')
class IndexView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def lot_status(self, lot):
        if lot.status == int(LotStatusEnum.New):
            return u"当選処理前"
        elif lot.status == int(LotStatusEnum.Lotting):
            return u"当落選択中"
        elif lot.status == int(LotStatusEnum.Electing):
            return u"当選処理実行中"
        elif lot.status == int(LotStatusEnum.Elected):
            return u"当選処理済み"
        elif lot.status == int(LotStatusEnum.Sent):
            # この状態は使ってない
            return u"当選処理前"
        return str(lot.status)

    @view_config(renderer='lots_admin/index.html')
    def __call__(self):
        """ 公開中、今後公開、終了した抽選
        公演、販売区分
        """

        organization_id = self.context.organization.id
        now = datetime.now()
        # 公開中
        lots = Lot.query.options(
            joinedload(Lot.event),
        ).join(
            Lot.sales_segment
        ).join(
            Lot.event
        ).join(
            Event.organization,
        ).filter(
            Organization.id==organization_id
        ).filter(
            SalesSegment.start_at<=now
        ).filter(
            SalesSegment.end_at>=now
        ).filter(
            ~Lot.is_finished(),
        ).order_by(Lot.lotting_announce_datetime).all()

        # 公開前
        post_lots = Lot.query.options(
            joinedload(Lot.event),
        ).join(
            Lot.sales_segment
        ).join(
            Lot.event
        ).join(
            Event.organization,
        ).filter(
            Organization.id==organization_id
        ).filter(
            SalesSegment.start_at>now
        ).filter(
            ~Lot.is_finished(),
        ).order_by(Lot.lotting_announce_datetime).all()

        # 公開終了
        past_lots = Lot.query.options(
            joinedload(Lot.event),
        ).join(
            Lot.sales_segment
        ).join(
            Lot.event
        ).join(
            Event.organization,
        ).filter(
            Organization.id==organization_id
        ).filter(
            SalesSegment.end_at<now
        ).filter(
            ~Lot.is_finished(),
        ).order_by(Lot.lotting_announce_datetime).all()

        return dict(lots=lots,
                    post_lots=post_lots,
                    past_lots=past_lots,
                    h=h,
                    eh=eh,
        )


@view_defaults(route_name='altair.app.ticketing.lots_admin.search',
               decorator=with_bootstrap, permission='event_editor')
class SearchLotsEntryView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create_form(self):

        form = SearchLotEntryForm(formdata=self.request.params)
        organization_id = self.context.organization.id
        lots = []
        if self.request.params.has_key('event') and self.request.params['event'] is not None :
            lots = Lot.query.join(
                Event.__table__,
                sql.and_(Event.id==Lot.event_id,
                         Event.deleted_at==None)).filter(
                             Event.organization_id==organization_id
                         ).filter(Event.id==self.request.params['event'])
        form.lot.choices = [('', '')] + [(str(l.id), l.name) for l in lots]

        events = Event.query.join(Event.setting) \
                            .filter(Event.organization_id==organization_id) \
                            .filter(EventSetting.visible==True) \
                            .order_by(Event.display_order)

        form.event.choices = [('', '')] + [(str(e.id), e.title) for e in events]
        return form

    @view_config(renderer="lots_admin/search.html")
    def __call__(self):
        """ 検索
        グローバルサーチなので、organizationの指定を慎重に。
        """
        organization_id = self.context.organization.id
        form = self.create_form()
        if self.request.params and form.validate():
            condition = (LotEntrySearch.id != None)
            if form.entry_no.data:
                condition = sql.and_(condition, LotEntrySearch.entry_no==form.entry_no.data)
            if form.tel.data:
                condition = sql.and_(condition,
                                     sql.or_(LotEntrySearch.shipping_address_tel_1==form.tel.data,
                                             LotEntrySearch.shipping_address_tel_2==form.tel.data))
            if form.name.data:
                condition = sql.and_(condition,
                                     sql.or_(LotEntrySearch.shipping_address_full_name==form.name.data,
                                             LotEntrySearch.shipping_address_last_name+LotEntrySearch.shipping_address_first_name==form.name.data,
                                             LotEntrySearch.shipping_address_last_name+" "+LotEntrySearch.shipping_address_first_name==form.name.data,
                                             LotEntrySearch.shipping_address_last_name==form.name.data,
                                             LotEntrySearch.shipping_address_first_name==form.name.data,
                                             LotEntrySearch.shipping_address_full_name_kana==form.name.data,
                                             LotEntrySearch.shipping_address_last_name_kana==form.name.data,
                                             LotEntrySearch.shipping_address_first_name_kana==form.name.data,))
            if form.email.data:
                condition = sql.and_(condition,
                                     sql.or_(LotEntrySearch.shipping_address_email_1==form.email.data,
                                             LotEntrySearch.shipping_address_email_2==form.email.data))

            if form.entried_from.data:
                condition = sql.and_(condition,
                                     LotEntrySearch.created_at>=form.entried_from.data)
            if form.entried_to.data:
                condition = sql.and_(condition,
                                     LotEntrySearch.created_at<=form.entried_to.data)
            if form.lot.data:
                condition = sql.and_(condition,
                                     LotEntrySearch.lot_id==form.lot.data)
            if form.event.data:
                condition = sql.and_(condition,
                                     LotEntrySearch.event_id==form.event.data)

            slave_session = get_db_session(self.request, name="slave")
            q = slave_session.query(LotEntrySearch).filter(
                LotEntrySearch.organization_id==organization_id,
                ).filter(
                condition
                )
            entries = q.all()
            count = q.count()
            page_url = PageURL_WebOb_Ex(self.request)

            page = paginate.Page(entries,
                                 page=self.request.GET.get('page', '1'),
                                 item_count=count,
                                 items_per_page=100,
                                 url=page_url)
        else:
            count = 0
            page = []
        return dict(organization_id=organization_id,
                    entries=page,
                    form=form,
                    count=count)

@view_defaults(xhr=True, permission='event_editor')
class LotsAPIView(BaseView):
    @view_config(renderer="json",route_name='api.lots_admin.event.lot')
    def get_lots(self):
        if self.request.params.has_key('event') and self.request.params['event'] is not None:
            event_id = self.request.params['event']
        else:
            return {"result":[], "status": False}
        query = Lot.query
        query = query.filter(Lot.event_id == event_id)
        lots = [
            dict(lotk='', name=u'(すべて)')]+[dict(lotk=lot.id, name='%s' % (lot.name))
            for lot in query]
        return {"result": lots, "status": True}
