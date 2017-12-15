# encoding: utf-8

import logging

from altair.app.ticketing.core.models import Event, Performance
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

        self._make_empty_first_4_digits_if_needed()
        self._upper_following_2to4_digits()

    def _upper_following_2to4_digits(self):
        """POSTされたパラメータを大文字に変更"""
        if 'following_2to4_digits' in self.request.POST:
            self.request.POST['following_2to4_digits'] = self.request.POST['following_2to4_digits'].upper()

    def _make_empty_first_4_digits_if_needed(self):
        """コード管理元が自社でなければ頭4文字は空にする"""
        if 'issued_by' in self.request.POST:
            if self.request.POST['issued_by'] != 'own':
                self.request.POST['first_digit'] = u''
                self.request.POST['following_2to4_digits'] = u''


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

    def event_pagination(self, event_title):
        """
        ページネーションによるイベントの取得とフォームの設定を返す
        LIKE検索がslaveでは実行できなかったので、masterを参照。
        """
        query = Event.query.filter(
            Event.organization_id == self.user.organization.id
        ).order_by(
            Event.display_order,
            Event.id.desc(),
        )

        if event_title:
            query = query.filter(Event.title.like(u"%{}%".format(event_title)))

        return query

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

        p_cnt = {}
        for r in result:
            p_cnt[r.event_id] = r.count

        return p_cnt

    def get_added_deleted_performance(self, added_id_list, deleted_id_list):
        """追加・削除対象のパフォーマンス情報の取得"""
        query = self.session.query(Performance).join(
            Event, Event.id == Performance.event_id
        ).order_by(
            Event.display_order,
            Event.id.desc(),
            Performance.display_order,
            Performance.start_on,
        )

        added = []
        if added_id_list:
            added = query.filter(
                Performance.id.in_(added_id_list)
            ).all()

        deleted = []
        if deleted_id_list:
            deleted = query.filter(
                Performance.id.in_(deleted_id_list)
            ).all()

        return added, deleted
