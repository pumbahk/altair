# encoding: utf-8

import logging

import webhelpers.paginate as paginate
from altair.app.ticketing.core.models import Event, Performance
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.discount_code.models import DiscountCodeTarget
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)


class DiscountCodeSettingResource(TicketingAdminResource):

    def __init__(self, request):
        super(DiscountCodeSettingResource, self).__init__(request)

        self.request = request
        self.session = get_db_session(request, name="slave")

        self._upper_following_2to4_digits()

    def _upper_following_2to4_digits(self):
        """POSTされたパラメータを大文字に変更"""
        if 'following_2to4_digits' in self.request.POST:
            self.request.POST['following_2to4_digits'] = self.request.POST['following_2to4_digits'].upper()


class DiscountCodeCodesResource(TicketingAdminResource):
    def __init__(self, request):
        super(DiscountCodeCodesResource, self).__init__(request)

        self.request = request
        self.session = get_db_session(request, name="slave")


class DiscountCodeTargetResource(TicketingAdminResource):
    def __init__(self, request):
        super(DiscountCodeTargetResource, self).__init__(request)

        self.request = request
        self.session = get_db_session(request, name="slave")
        self.setting_id = request.matchdict['setting_id']

    def event_pagination(self, f):
        """
        ページネーションの範囲内のイベント情報の取得。
        LIKE検索がslaveでは実行できなかったので、masterを参照。
        """
        query = Event.query.filter(
            Event.organization_id == self.user.organization.id
        ).order_by(
            Event.display_order,
            Event.id.desc(),
        )

        event_title = f.data['event_title']
        if event_title:
            query = query.filter(Event.title.like(u"%{}%".format(event_title)))

        events = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )

        return events

    @staticmethod
    def get_event_id_list(events):
        """ページネーションの範囲内のイベントID取得"""
        event_id_list = []
        for event in events:
            event_id_list.append(event.id)

        return event_id_list

    def get_registered_id_list(self, event_id_list):
        """ページネーションの範囲内の登録済パフォーマンスIDを取得"""
        result = self.session.query(DiscountCodeTarget).filter(
            DiscountCodeTarget.event_id.in_(event_id_list),
            DiscountCodeTarget.discount_code_setting_id == self.setting_id
        ).order_by(
            DiscountCodeTarget.performance_id
        ).all()

        registered = []
        for r in result:
            registered.append(unicode(r.performance_id))

        return registered

    def registered_performance_num_of_each_events(self, event_id_list):
        """ページネーションの範囲内のイベントの設定済パフォーマンス数取得"""
        result = self.session.query(DiscountCodeTarget).add_columns(
            DiscountCodeTarget.event_id,
            func.count(DiscountCodeTarget.performance_id).label("count"),
        ).filter(
            DiscountCodeTarget.event_id.in_(event_id_list),
            DiscountCodeTarget.discount_code_setting_id == self.setting_id
        ).group_by(
            DiscountCodeTarget.event_id
        ).all()

        performance_count = {}
        for r in result:
            performance_count[r.event_id] = r.count

        return performance_count

    def get_performance_from_id_list(self, id_list):
        """IDからパフォーマンス情報の取得"""
        query = self.session.query(Performance).join(
            Event, Event.id == Performance.event_id
        ).order_by(
            Event.display_order,
            Event.id.desc(),
            Performance.start_on,
        )

        performances = []
        if len(id_list) != 0:
            performances = query.filter(
                Performance.id.in_(id_list)
            ).all()

        return performances

    def get_discount_target_from_id_list(self, id_list):
        """IDから割引コード適用対象の取得"""
        targets = []
        if len(id_list) != 0:
            targets = DiscountCodeTarget.query.filter(
                DiscountCodeTarget.performance_id.in_(id_list),
                DiscountCodeTarget.discount_code_setting_id == self.setting_id
            ).all()

        return targets
