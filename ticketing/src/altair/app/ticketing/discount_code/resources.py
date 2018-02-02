# -*- coding: utf-8 -*-

import logging

import webhelpers.paginate as paginate
from altair.app.ticketing.core.models import Event, Performance
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.discount_code.models import DiscountCodeTarget, DiscountCodeCode
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from sqlalchemy.sql import and_
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)


class DiscountCodeSettingResource(TicketingAdminResource):
    def __init__(self, request):
        super(DiscountCodeSettingResource, self).__init__(request)

        self.request = request
        self.session = get_db_session(request, name="slave")

        self._upper_following_2to4_digits()
        self._make_empty_first_4_digits_if_needed()

    def _upper_following_2to4_digits(self):
        """POSTされたパラメータを大文字に変更"""
        if 'following_2to4_digits' in self.request.POST:
            self.request.POST['following_2to4_digits'] = self.request.POST['following_2to4_digits'].upper()

    def _make_empty_first_4_digits_if_needed(self):
        """コード管理元が自社でなければ有効期間は空にする"""
        if 'issued_by' in self.request.POST:
            if self.request.POST['issued_by'] != 'own':
                at_list = ['start_at', 'end_at']
                unit_list = ['year', 'month', 'day', 'hour', 'minute']
                for at in at_list:
                    for unit in unit_list:
                        self.request.POST['{}.{}'.format(at, unit)] = u''

    def delete_discount_code_setting(self, setting):
        # TODO 削除を禁止する各条件を後々で用意する

        for code in setting.DiscountCode:
            code.delete()

        for target in setting.DiscountCodeTarget:
            target.delete()

        setting.delete()


class DiscountCodeCodesResource(TicketingAdminResource):
    def __init__(self, request):
        super(DiscountCodeCodesResource, self).__init__(request)

        self.request = request
        self.session = get_db_session(request, name="slave")
        self.setting_id = request.matchdict['setting_id']

    def code_pagination(self, sf):
        """
        ページネーションの範囲内のクーポン・割引コード情報の取得
        :param SearchCodeForm sf: オブジェクト
        :return Page codes: 表示しようとしているページ分のコード情報 （webhelpers.paginate._SQLAlchemyQuery）
        """
        query = self.code_index_search_query(sf)

        codes = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )

        return codes

    def code_index_search_query(self, f):
        """コード一覧の検索条件を含むデータ抽出クエリ"""
        query = self.session.query(DiscountCodeCode).filter(
            DiscountCodeCode.discount_code_setting_id == self.setting_id,
            DiscountCodeCode.organization_id == self.user.organization.id
        )

        sort = self.request.GET.get('sort', 'id')
        direction = self.request.GET.get('direction', 'asc')
        query = query.order_by('{0} {1}'.format(sort, direction))

        if f.data['code']:
            query = query.filter(DiscountCodeCode.code == f.data['code'].strip())

        return query


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

        if f.data['event_title']:
            query = query.filter(Event.title.like(u"%{}%".format(f.data['event_title'].strip())))

        if f.data['only_existing_target_event']:
            query = query.join(
                DiscountCodeTarget,
                and_(Event.id == DiscountCodeTarget.event_id,
                     DiscountCodeTarget.discount_code_setting_id == self.setting_id)
            ).group_by(Event.id)

        events = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )

        events = self._add_other_discount_code_setting_names_for_each_performances(events)

        return events

    def _add_other_discount_code_setting_names_for_each_performances(self, events):
        """
        各公演に設定済みのクーポン・割引コード設定名を付加する。
        画面表示をリクエストされている自身の設定名は除く。
        :param events: イベント情報
        :return events: リスト「other_discount_code_setting_names」の付加
        """
        own_setting_id = self.request.matchdict['setting_id']
        for event in events:
            for performance in event.performances:
                others = []
                for target in performance.DiscountCodeTarget:
                    if unicode(target.discount_code_setting_id) != own_setting_id:
                        others.append(target.discount_code_setting.name)
                performance.other_discount_code_setting_names = others

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
