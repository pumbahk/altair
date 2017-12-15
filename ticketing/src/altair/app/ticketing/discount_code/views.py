# encoding: utf-8

import json
import logging

import webhelpers.paginate as paginate
from altair.app.ticketing.core.models import Event, Performance
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.views import BaseView
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPInternalServerError
from pyramid.renderers import render_to_response
from pyramid.view import view_config, view_defaults
from sqlalchemy.sql import func
from .api import is_enabled_discount_code_checked, get_discount_setting_related_data
from .forms import DiscountCodeSettingForm, DiscountCodeCodesForm, SearchTargetForm
from .models import DiscountCodeSetting, DiscountCodeCode, DiscountCodeTarget, delete_discount_code_setting

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap,
               permission='event_editor',
               custom_predicates=(is_enabled_discount_code_checked,))
class DiscountCode(BaseView):
    @view_config(route_name='discount_code.settings_index',
                 renderer='altair.app.ticketing:templates/discount_code/settings/index.html', permission='event_viewer')
    def settings_index(self):
        sort = self.request.GET.get('sort', 'DiscountCodeSetting.end_at')
        direction = self.request.GET.get('direction', 'desc')

        query = self.context.session.query(DiscountCodeSetting).filter_by(
            organization_id=self.context.user.organization_id)
        query = query.order_by('{0} {1}'.format(sort, direction)) \
            .order_by('DiscountCodeSetting.id desc')

        settings = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=PageURL_WebOb_Ex(self.request)
        )

        return {
            'form': DiscountCodeSettingForm(),
            'settings': settings,
        }

    @view_config(route_name='discount_code.settings_new', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/settings/_form.html', xhr=True)
    def settings_new(self):
        f = DiscountCodeSettingForm()
        return {
            'form': f,
            'action': self.request.path,
        }

    @view_config(route_name='discount_code.settings_new', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/settings/_form.html', xhr=True)
    def settings_new_post(self):
        f = DiscountCodeSettingForm(self.request.POST, organization_id=self.context.user.organization.id)

        if f.validate():
            setting = DiscountCodeSetting(
                is_valid=f.data['is_valid'],
                organization_id=self.context.user.organization.id,
                name=f.data['name'],
                issued_by=f.data['issued_by'],
                first_digit=f.data['first_digit'],
                following_2to4_digits=f.data['following_2to4_digits'].upper(),
                criterion=f.data['criterion'],
                condition_price_amount=f.data['condition_price_amount'],
                condition_price_more_or_less=f.data['condition_price_more_or_less'],
                benefit_amount=f.data['benefit_amount'],
                benefit_unit=f.data['benefit_unit'],
                start_at=f.data['start_at'],
                end_at=f.data['end_at'],
                explanation=f.data['explanation'],
            )
            setting.save()

            self.request.session.flash(u'クーポン・割引コード設定を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'action': self.request.path,
            }

    @view_config(route_name='discount_code.settings_edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/settings/_form.html', xhr=True)
    def settings_edit(self):
        setting_id = int(self.request.matchdict.get('setting_id', 0))
        setting = self.context.session.query(DiscountCodeSetting).filter_by(id=setting_id).filter_by(
            organization_id=self.context.user.organization_id).first()
        if setting is None:
            return HTTPNotFound('setting id %d is not found' % setting_id)

        f = DiscountCodeSettingForm(obj=setting)
        return {
            'form': f,
            'action': self.request.path,
        }

    @view_config(route_name='discount_code.settings_edit', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/settings/_form.html', xhr=True)
    def settings_edit_post(self):
        setting_id = int(self.request.matchdict.get('setting_id', 0))
        setting = DiscountCodeSetting.query.filter_by(id=setting_id).filter_by(
            organization_id=self.context.user.organization_id).first()
        if setting is None:
            return HTTPNotFound('setting id %d is not found' % setting_id)

        f = DiscountCodeSettingForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            setting = merge_session_with_post(setting, f.data)
            setting.organization_id = self.context.user.organization.id
            setting.save()

            self.request.session.flash(u'クーポン・割引コード設定を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'action': self.request.path,
            }

    @view_config(route_name='discount_code.settings_delete')
    def settings_delete(self):
        location = self.request.route_path('discount_code.settings_index')
        setting_id = int(self.request.matchdict.get('setting_id', 0))
        setting = DiscountCodeSetting.get(setting_id, organization_id=self.context.user.organization_id)
        if setting is None:
            return HTTPNotFound('discount_code_setting_id %d is not found' % setting_id)

        try:
            delete_discount_code_setting(setting)
            self.request.session.flash(u'クーポン・割引コード設定を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

    @view_config(route_name='discount_code.codes_index',
                 renderer='altair.app.ticketing:templates/discount_code/codes/index.html', permission='event_viewer',
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_index(self):
        return {
            'form': DiscountCodeCodesForm(),
            'setting': self.context.setting,
            'codes': self.context.setting.code
        }

    @view_config(route_name='discount_code.codes_add', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/codes/_form.html', xhr=True,
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_add(self):
        f = DiscountCodeCodesForm()
        return {
            'form': f,
            'setting': self.context.setting,
            'codes': self.context.setting.code,
            'action': self.request.path,
        }

    @view_config(route_name='discount_code.codes_add', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/codes/_form.html', xhr=True,
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_add_post(self):
        self.request.POST['code'] = 'TIK78329SEGE'
        f = DiscountCodeCodesForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            code = DiscountCodeCode(
                discount_code_setting_id=self.context.setting.id,
                organization_id=self.context.user.organization.id,
                operator_id=self.request.context.user.id,
                code=f.data['code'],
            )
            code.save()

            self.request.session.flash(u'クーポン・割引コードを1件追加しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'setting': self.context.setting,
                'codes': self.context.setting.code,
                'action': self.request.path,
            }

    @view_config(route_name='discount_code.codes_delete_all', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/codes/_form.html', xhr=True,
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_delete_all(self):
        pass

    @view_config(route_name='discount_code.codes_csv_export', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/codes/_form.html',
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_csv_export(self):
        pass

    def _event_pagination(self, setting_id, organization_id):
        """
        ページネーションによるイベントの取得とフォームの設定を返す
        LIKE検索がslaveでは実行できなかったので、masterを参照。
        """
        query = Event.query.filter(
            Event.organization_id == organization_id
        ).order_by(
            Event.display_order,
            Event.id.desc(),
        )

        f = SearchTargetForm(self.request.GET, organization_id=organization_id)
        if f.validate():
            event_title = f.data['event_title']
            if event_title:
                query = query.filter(Event.title.like(u"%%%s%%" % event_title))

        events = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )

        return f, events

    @view_config(route_name='discount_code.target_index',
                 renderer='altair.app.ticketing:templates/discount_code/target/index.html', permission='event_viewer',
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def target_index(self):
        f, events = self._event_pagination(setting_id=self.context.setting.id,
                                           organization_id=self.context.user.organization_id)

        event_id_list = self._get_event_id_list(events)
        registered = self._get_registered_id_list(event_id_list)
        p_cnt, total_p_cnt = self._registered_performance_num_of_each_events(event_id_list)

        return {
            'setting': self.context.setting,
            'events': events,
            'registered': registered,
            'p_cnt': p_cnt,
            'total_p_cnt': total_p_cnt,
            'search_form': f
        }

    @view_config(route_name='discount_code.target_confirm',
                 renderer='altair.app.ticketing:templates/discount_code/target/_modal.html', permission='event_viewer',
                 xhr=True,
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def target_confirm(self):
        """すでに登録されている適用対象と、今回の登録内容を比較し、どのパフォーマンスが追加・削除されたか表示する"""
        f, events = self._event_pagination(setting_id=self.context.setting.id,
                                           organization_id=self.context.user.organization_id)

        event_id_list = self._get_event_id_list(events)
        registered = self._get_registered_id_list(event_id_list)

        performance_id_list = self.request.params['performance_id_list']
        selected_list = json.loads(performance_id_list)

        added_id_list = list(set(selected_list) - set(registered))
        deleted_id_list = list(set(registered) - set(selected_list))

        added, deleted = self._get_added_deleted_performance(added_id_list, deleted_id_list)

        return {
            'setting': self.context.setting,
            'registered': registered,
            'added': added,
            'deleted': deleted,
            'performance_id_list': performance_id_list,
            'added_id_list': json.dumps(added_id_list),
            'deleted_id_list': json.dumps(deleted_id_list),
        }

    @view_config(route_name='discount_code.target_register', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/target/_modal.html', permission='event_viewer',
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def target_register(self):
        added_id_list = self.request.params['added_id_list']
        deleted_id_list = self.request.params['deleted_id_list']

        logger.info('Update discount code target performance(s). '
                    'operator_id: {}, '
                    'added_id_list: {}, '
                    'deleted_id_list: {}'.format(self.context.user.id, added_id_list, deleted_id_list)
                    )

        added = []
        if added_id_list:
            added = self.context.session.query(Performance).filter(
                Performance.id.in_(json.loads(added_id_list))
            ).order_by(
                Performance.event_id.desc(),
                Performance.end_on.desc(),
                Performance.start_on.desc()
            ).all()

        deleted = []
        if deleted_id_list:
            deleted = DiscountCodeTarget.query.filter(
                DiscountCodeTarget.performance_id.in_(json.loads(deleted_id_list))
            ).all()

        try:
            for add in added:
                target = DiscountCodeTarget(
                    discount_code_setting_id=self.context.setting.id,
                    event_id=add.event.id,
                    performance_id=add.id
                )
                target.save()

            for delete in deleted:
                delete.delete()

        except Exception as e:
            logger.error(
                'Failed to update discount code target performance(s). '
                'error_message: {}'.format(
                    str(e.message)
                )
            )
            return HTTPInternalServerError()

        self.request.session.flash(u'変更内容を保存しました')
        return HTTPFound(self.request.route_path("discount_code.target_index", setting_id=self.context.setting.id,
                                                 _query=self.request.GET))

    @staticmethod
    def _get_event_id_list(events):
        """ページネーションの範囲内のイベントID取得"""
        event_id_list = []
        for event in events:
            event_id_list.append(event.id)

        return event_id_list

    def _get_registered_id_list(self, event_id_list):
        """ページネーションの範囲内の登録済パフォーマンスIDを取得"""
        result = self.context.session.query(DiscountCodeTarget).filter(
            DiscountCodeTarget.event_id.in_(event_id_list),
            DiscountCodeTarget.discount_code_setting_id == self.context.setting.id
        ).order_by(
            DiscountCodeTarget.performance_id
        ).all()

        registered = []
        for r in result:
            registered.append(unicode(r.performance_id))

        return registered

    def _registered_performance_num_of_each_events(self, event_id_list):
        """ページネーションの範囲内のイベントの設定済パフォーマンス数取得"""
        result = self.context.session.query(DiscountCodeTarget).add_columns(
            DiscountCodeTarget.event_id,
            func.count(DiscountCodeTarget.performance_id).label("count"),
        ).filter(
            DiscountCodeTarget.event_id.in_(event_id_list),
            DiscountCodeTarget.discount_code_setting_id == self.context.setting.id
        ).group_by(
            DiscountCodeTarget.event_id
        ).all()

        total_p_cnt = 0
        p_cnt = {}
        for r in result:
            total_p_cnt = total_p_cnt + int(r.count)
            p_cnt[r.event_id] = r.count

        return p_cnt, total_p_cnt

    def _get_added_deleted_performance(self, added_id_list, deleted_id_list):
        """追加・削除対象のパフォーマンス情報の取得"""
        query = self.context.session.query(Performance).join(
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
