# -*- coding: utf-8 -*-

import json
import logging
import time
import urllib
from datetime import datetime

import webhelpers.paginate as paginate
from altair.app.ticketing.utils import get_safe_filename
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.views import BaseView
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPInternalServerError
from pyramid.renderers import render_to_response
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy.exc import SQLAlchemyError
from .api import is_enabled_discount_code_checked, get_discount_setting_related_data
from .forms import DiscountCodeSettingForm, DiscountCodeCodesForm, SearchTargetForm, SearchCodeForm
from .models import DiscountCodeSetting, DiscountCodeCode, DiscountCodeTarget, delete_discount_code_setting, \
    delete_all_discount_code, insert_code_by_alchemy_orm

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
        setting_id = int(self.request.matchdict.get('setting_id', 0))
        setting = DiscountCodeSetting.get(setting_id, organization_id=self.context.user.organization_id)
        if setting is None:
            return HTTPNotFound('discount_code_setting_id %d is not found' % setting_id)

        try:
            delete_discount_code_setting(setting)
            self.request.session.flash(u'クーポン・割引コード設定を削除しました')
        except SQLAlchemyError as e:
            self.request.session.flash(u'クーポン・割引コード設定の削除に失敗しました')

        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='discount_code.codes_index',
                 renderer='altair.app.ticketing:templates/discount_code/codes/index.html', permission='event_viewer',
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_index(self):
        f = SearchCodeForm(self.request.GET, organization_id=self.context.organization.id)
        if f.validate():
            codes = self.context.code_pagination(f)
            return {
                'search_form': f,
                'setting': self.context.setting,
                'codes': codes
            }
        else:
            self.request.session.flash(u'検索条件に不備があります')
            return HTTPFound(self.request.route_path("discount_code.codes_index", setting_id=self.context.setting_id,
                                                     _query=self.request.GET))

    @view_config(route_name='discount_code.codes_csv_export',
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_csv_export(self):
        f = SearchCodeForm(self.request.GET, organization_id=self.context.organization.id)
        if f.validate():
            codes = self.context.code_index_search_query(f).all()

            render_param = dict(codes=codes)
            r = render_to_response('altair.app.ticketing:templates/discount_code/codes/export.txt', render_param,
                                   request=self.request)
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = u"{}_code_list_{}.csv".format(get_safe_filename(self.context.setting.name), now)
            headers = [
                ('Content-Type', 'application/octet-stream; charset=utf-8'),
                ('Content-Disposition', "attachment; filename*=utf-8''%s" % urllib.quote(filename.encode("utf-8")))
            ]
            return Response(r.text.encode('cp932'), headers=headers)

        else:
            self.request.session.flash(u'検索条件に不備があります')
            return HTTPFound(self.request.route_path("discount_code.codes_index", setting_id=self.context.setting_id,
                                                     _query=self.request.GET))

    @view_config(route_name='discount_code.codes_add', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/codes/_form.html', xhr=True,
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_add(self):
        f = DiscountCodeCodesForm()
        return {
            'form': f,
            'setting': self.context.setting,
            'action': self.request.path,
        }

    @view_config(route_name='discount_code.codes_add', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/codes/_form.html', xhr=True,
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def codes_add_post(self):
        """
        12桁の英数字（使用可能文字：[A,C,E-H,K-N,P-R,T,W-Y,3,4,6,7,9]）を指定数分生成
        頭4桁は設定で固定される（例: TST8）。
        22の8乗 = 54,875,873,536通りのコードが作成できる。

        :see "Coupon Code Issue Rule" https://rak.app.box.com/notes/249136006452
        """
        f = DiscountCodeCodesForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            num = f.data['generate_num']
            first_4_digits = self.context.setting.first_4_digits
            data = {
                'discount_code_setting_id': self.context.setting.id,
                'organization_id': self.context.user.organization.id,
                'operator_id': self.request.context.user.id,
            }

            t0 = time.time()
            if insert_code_by_alchemy_orm(num, first_4_digits, data):
                self.request.session.flash(u'クーポン・割引コードを{}件追加しました'.format(num))
            else:
                self.request.session.flash(u'コード生成中にエラーが発生しました')

            logger.info(u"execution time {} sec".format(str(time.time() - t0)))
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

        else:
            return {
                'form': f,
                'setting': self.context.setting,
                'action': self.request.path,
            }

    @view_config(route_name='discount_code.codes_delete_all')
    def codes_delete_all(self):
        setting_id = int(self.request.matchdict.get('setting_id', 0))
        location = self.request.route_path('discount_code.codes_index', setting_id=setting_id)
        setting = DiscountCodeSetting.get(setting_id, organization_id=self.context.user.organization_id)
        if setting is None:
            return HTTPNotFound('discount_code_setting_id %d is not found' % setting_id)

        t0 = time.time()
        try:
            deleted_num = delete_all_discount_code(setting.id)
            if deleted_num != 0:
                self.request.session.flash(u'コードを全削除しました（{}件）'.format(deleted_num))
            else:
                self.request.session.flash(u'削除対象が存在しません')

        except SQLAlchemyError:
            self.request.session.flash(u'コードの全削除に失敗しました')

        logger.info(u"execution time {} sec".format(str(time.time() - t0)))
        return HTTPFound(location=location)

    @view_config(route_name='discount_code.codes_used_at')
    def codes_used_at(self):
        setting_id = int(self.request.matchdict.get('setting_id', 0))
        code_id = int(self.request.matchdict.get('code_id', 0))

        try:
            code = DiscountCodeCode.filter_by(
                id=code_id,
                discount_code_setting_id=setting_id,
                organization_id=self.context.user.organization_id
            ).first()

            if code is None:
                return HTTPNotFound('code_id {} is not found'.format(code_id))
            elif code.used_at:
                self.request.session.flash(u'コードID: {}はすでに使用済みです'.format(code.id))
            else:
                code.used_at = datetime.now()
                code.operator_id = self.request.context.user.id
                code.save()
                self.request.session.flash(u'コードID: {}を使用済みにしました'.format(code.id))

        except SQLAlchemyError:
            self.request.session.flash(u'システムエラーが発生しました')

        return HTTPFound(self.request.route_path("discount_code.codes_index", setting_id=self.context.setting_id,
                                                 _query=self.request.GET))

    @view_config(route_name='discount_code.target_index',
                 renderer='altair.app.ticketing:templates/discount_code/target/index.html', permission='event_viewer',
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def target_index(self):
        f = SearchTargetForm(self.request.GET, organization_id=self.context.organization.id)
        if f.validate():
            events = self.context.event_pagination(f)
            event_id_list = self.context.get_event_id_list(events)
            registered = self.context.get_registered_id_list(event_id_list)

            performance_count = self.context.registered_performance_num_of_each_events(event_id_list)

            return {
                'setting': self.context.setting,
                'events': events,
                'registered': registered,
                'performance_count': performance_count,
                'search_form': f
            }

        else:
            self.request.session.flash(u'検索条件に不備があります')
            return HTTPFound(self.request.route_path("discount_code.target_index", setting_id=self.context.setting.id,
                                                     _query=self.request.GET))

    @view_config(route_name='discount_code.target_confirm',
                 renderer='altair.app.ticketing:templates/discount_code/target/_modal.html', permission='event_viewer',
                 xhr=True,
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def target_confirm(self):
        """すでに登録されている適用対象と、今回の登録内容を比較し、どのパフォーマンスが追加・削除されたか表示する"""
        f = SearchTargetForm(self.request.GET, organization_id=self.context.organization.id)
        if f.validate():
            events = self.context.event_pagination(f)
            event_id_list = self.context.get_event_id_list(events)
            registered = self.context.get_registered_id_list(event_id_list)

            selected_list = json.loads(self.request.params['performance_id_list'])
            selected_list = filter(lambda a: a != 'on', selected_list)  # 全選択にチェックが入ると'on'が含まれるので除去

            added_id_list = list(set(selected_list) - set(registered))
            deleted_id_list = list(set(registered) - set(selected_list))

            added = self.context.get_performance_from_id_list(added_id_list)
            deleted = self.context.get_performance_from_id_list(deleted_id_list)

            return {
                'setting': self.context.setting,
                'registered': registered,
                'added': added,
                'deleted': deleted,
                'added_id_list': json.dumps(added_id_list),
                'deleted_id_list': json.dumps(deleted_id_list),
            }

        else:
            self.request.session.flash(u'検索条件に不備があります')
            return HTTPFound(self.request.route_path("discount_code.target_index", setting_id=self.context.setting.id,
                                                     _query=self.request.GET))

    @view_config(route_name='discount_code.target_register', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/target/_modal.html', permission='event_viewer',
                 custom_predicates=(is_enabled_discount_code_checked, get_discount_setting_related_data,))
    def target_register(self):
        logger.info(
            'Update discount code target performance(s).operator_id: {}, added_id_list: {}, deleted_id_list: {}'.format(
                self.context.user.id,
                self.request.params['added_id_list'],
                self.request.params['deleted_id_list']
            )
        )

        added_id_list = json.loads(self.request.params['added_id_list'])
        deleted_id_list = json.loads(self.request.params['deleted_id_list'])

        added = self.context.get_performance_from_id_list(added_id_list)
        deleted = self.context.get_discount_target_from_id_list(deleted_id_list)

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

        except SQLAlchemyError as e:
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
