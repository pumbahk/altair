# -*- coding:utf-8 -*-
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
from altair.app.ticketing.models import (
    DBSession,
)
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import (
    SalesSegment,
    Event,
    Organization,
)

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

@view_defaults(route_name='altair.app.ticketing.lots_admin.index',
               decorator=with_bootstrap)
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
        )


@view_defaults(route_name='altair.app.ticketing.lots_admin.search',
               decorator=with_bootstrap)
class SearchLotsEntryView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create_form(self):

        form = SearchLotEntryForm(formdata=self.request.params)
        organization_id = self.context.organization.id
        lots = Lot.query.join(
            Event.__table__,
            sql.and_(Event.id==Lot.event_id,
                     Event.deleted_at==None)).filter(
            Event.organization_id==organization_id
            )
        form.lot.choices = [('', '')] + [(str(l.id), l.event.title + "/" + l.name)
                     for l in lots]
        return form

    @view_config(renderer="lots_admin/search.html")
    def __call__(self):
        """ 検索 
        グローバルサーチなので、organizationの指定を慎重に。
        """

        organization_id = self.context.organization.id
        form = self.create_form()
        condition = (LotEntrySearch.id != None)
        if form.validate():
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

        q = DBSession.query(LotEntrySearch).filter(
            LotEntrySearch.organization_id==organization_id,
            ).filter(
            condition
            )
        entries = q.all()
        count = q.count()
        page_url = paginate.PageURL_WebOb(self.request)

        page = paginate.Page(entries,
                             page=self.request.GET.get('page', '1'),
                             item_count=count,
                             items_per_page=100,
                             url=page_url)
        return dict(organization_id=organization_id,
                    #entries=entries,
                    entries=page,
                    form=form,
                    count=count)
