# -*- coding: utf-8 -*-

import json
import logging
import time
import urllib
from datetime import datetime

from altair.app.ticketing.core.models import Event, Performance
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.discount_code import util
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.utils import get_safe_filename
from altair.app.ticketing.views import BaseView
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPInternalServerError
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from sqlalchemy.exc import SQLAlchemyError
from webhelpers import paginate
from .forms import (DiscountCodeSettingForm, DiscountCodeCodesForm, SearchTargetForm, SearchCodeForm,
                    DiscountCodeTargetStForm, SearchTargetStForm)
from .models import (DiscountCodeSetting, DiscountCodeCode, DiscountCodeTarget, DiscountCodeTargetStockType)

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap,
               permission='master_editor',
               custom_predicates=(util.check_discount_code_functions_available,))
class DiscountCode(BaseView):
    @view_config(route_name='discount_code.settings_index',
                 renderer='altair.app.ticketing:templates/discount_code/settings/index.html')
    def settings_index(self):
        query = self.context.session.query(DiscountCodeSetting).filter_by(
            organization_id=self.context.user.organization_id)

        return {
            'form': DiscountCodeSettingForm(),
            'settings': util.paginate_setting_list(query, self.request),
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
        setting_id = int(self.request.matchdict.get('setting_id'))
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
        setting_id = int(self.request.matchdict.get('setting_id'))
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
        setting_id = int(self.request.matchdict.get('setting_id'))
        setting = DiscountCodeSetting.get(setting_id, organization_id=self.context.user.organization_id)
        if setting is None:
            return HTTPNotFound('discount_code_setting_id %d is not found' % setting_id)

        err_reasons = util.validate_to_delete_all_codes(setting, self.context.session)
        if err_reasons:
            self.request.session.flash(
                u'「ID:{} {}」を削除できません（{}）'.format(setting.id, setting.name, u'・'.join(err_reasons)))
            return HTTPFound(location=self.request.referer)
        try:
            self.context.delete_discount_code_setting(setting)
            self.request.session.flash(u'「ID:{} {}」を削除しました'.format(setting.id, setting.name))
        except SQLAlchemyError as e:
            self.request.session.flash(u'「ID:{} {}」の削除に失敗しました'.format(setting.id, setting.name))
            logger.error("Couldn't delete discount_code_setting: {}".format(str(e)))

        return HTTPFound(location=self.request.referer)

    @view_config(route_name='discount_code.codes_index',
                 renderer='altair.app.ticketing:templates/discount_code/codes/index.html')
    def codes_index(self):
        f = DiscountCodeCodesForm()
        sf = SearchCodeForm(self.request.GET, organization_id=self.context.organization.id)
        if sf.validate():
            codes = self.context.code_pagination(sf)
            return {
                'form': f,
                'search_form': sf,
                'setting': self.context.setting,
                'codes': codes
            }
        else:
            self.request.session.flash(u'検索条件に不備があります')
            return HTTPFound(self.request.route_path("discount_code.codes_index", setting_id=self.context.setting_id,
                                                     _query=self.request.GET))

    @view_config(route_name='discount_code.codes_csv_export')
    def codes_csv_export(self):
        f = SearchCodeForm(self.request.GET, organization_id=self.context.organization.id)
        if f.validate():
            t0 = time.time()
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
            logger.info("number of codes: {}, execution time {} sec".format(len(codes), str(time.time() - t0)))
            return Response(r.text.encode('cp932'), headers=headers)

        else:
            self.request.session.flash(u'検索条件に不備があります')
            return HTTPFound(self.request.route_path("discount_code.codes_index", setting_id=self.context.setting_id,
                                                     _query=self.request.GET))

    @view_config(route_name='discount_code.codes_add', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/codes/_form.html', xhr=True)
    def codes_add(self):
        f = DiscountCodeCodesForm()
        return {
            'form': f,
            'setting': self.context.setting,
            'action': self.request.path,
        }

    @view_config(route_name='discount_code.codes_add', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/codes/_form.html', xhr=True)
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
            try:
                util.insert_specific_number_code(num, first_4_digits, data)
            except SQLAlchemyError as e:
                logger.error(
                    'Failed to create discount codes. '
                    'base_data: {} '
                    'error_message: {}'.format(
                        str(data),
                        str(e.message)
                    )
                )
                self.request.session.flash(u'コード生成中にエラーが発生しました')

            logger.info("execution time {} sec".format(str(time.time() - t0)))
            self.request.session.flash(u'クーポン・割引コードを{}件追加しました'.format(num))
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

        else:
            return {
                'form': f,
                'setting': self.context.setting,
                'action': self.request.path,
            }

    @view_config(route_name='discount_code.codes_delete_all')
    def codes_delete_all(self):
        setting_id = int(self.request.matchdict.get('setting_id'))
        location = self.request.route_path('discount_code.codes_index', setting_id=setting_id)
        setting = DiscountCodeSetting.get(setting_id, organization_id=self.context.user.organization_id)
        if setting is None:
            return HTTPNotFound('discount_code_setting_id %d is not found' % setting_id)

        err_reasons = util.validate_to_delete_all_codes(setting, self.context.session)
        if err_reasons:
            self.request.session.flash(
                u'「ID:{} {}」を削除できません（{}）'.format(setting.id, setting.name, u'・'.join(err_reasons)))
            return HTTPFound(location=location)

        try:
            deleted_num = util.delete_all_discount_code(setting.id)
            if deleted_num != 0:
                logger.info('All codes belongs to DiscountCodeSetting.id: {} was deleted by Operator.id {}'.format(
                    setting.id,
                    self.context.user.id
                ))
                self.request.session.flash(u'コードを全削除しました（{}件）'.format(deleted_num))
            else:
                self.request.session.flash(u'削除対象が存在しません')

        except SQLAlchemyError:
            self.request.session.flash(u'コードの全削除に失敗しました')

        return HTTPFound(location=location)

    @view_config(route_name='discount_code.codes_used_at')
    def codes_used_at(self):
        setting_id = int(self.request.matchdict.get('setting_id'))
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
                logger.info(
                    'Code ID: {} was made its status "used" by Operator.id: {}'.format(code.id, self.context.user.id))
                self.request.session.flash(u'コードID: {}を使用済みにしました'.format(code.id))

        except SQLAlchemyError:
            self.request.session.flash(u'システムエラーが発生しました')

        return HTTPFound(self.request.route_path("discount_code.codes_index", setting_id=self.context.setting_id,
                                                 _query=self.request.GET))

    @view_config(route_name='discount_code.target_index',
                 renderer='altair.app.ticketing:templates/discount_code/target/index.html')
    def target_index(self):
        f = SearchTargetForm(self.request.GET, organization_id=self.context.organization.id)
        if f.validate():
            query = self.context.event_pagination_query(f, self.context.session)
            event_cnt = query.count()
            events = self.context.event_pagination(query)
            event_id_list = self.context.get_event_id_list(events)
            registered = self.context.get_registered_id_list(event_id_list)

            performance_count = self.context.registered_performance_num_of_each_events(event_id_list)

            return {
                'setting': self.context.setting,
                'events': events,
                'event_cnt': event_cnt,
                'registered': registered,
                'performance_count': performance_count,
                'search_form': f
            }

        else:
            self.request.session.flash(u'検索条件に不備があります')
            return HTTPFound(self.request.route_path("discount_code.target_index", setting_id=self.context.setting.id,
                                                     _query=self.request.GET))

    @view_config(route_name='discount_code.target_confirm',
                 renderer='altair.app.ticketing:templates/discount_code/target/_modal.html',
                 xhr=True)
    def target_confirm(self):
        """すでに登録されている適用公演と、今回の登録内容を比較し、どのパフォーマンスが追加・削除されたか表示する"""
        f = SearchTargetForm(self.request.GET, organization_id=self.context.organization.id)
        if f.validate():
            query = self.context.event_pagination_query(f, self.context.session)
            events = self.context.event_pagination(query)
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
                 renderer='altair.app.ticketing:templates/discount_code/target/_modal.html')
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

    @view_config(route_name='discount_code.target_st_index',
                 request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/target_st/index.html')
    def target_st_index_get(self):
        # 検索フォーム
        search_form = SearchTargetStForm(self.request.GET, organization_id=self.context.organization.id)
        if search_form.validate():
            # 「設定済の席種」公演の基本クエリ
            query = util.get_performances_of_dc_setting(self.context.session, self.context.setting_id)

            # 検索条件追加
            if search_form.data['event_id']:
                query = query.filter(Event.id == search_form.data['event_id'])
            if search_form.data['performance_id']:
                query = query.filter(Performance.id == search_form.data['performance_id'])

            # ページネーション
            performances = paginate.Page(
                query,
                page=int(self.context.request.params.get('page', 0)),
                items_per_page=20,
                url=PageURL_WebOb_Ex(self.context.request)
            )

            # 公演とクーポン・割引コード設定に紐づく登録済適用席種情報の取得クエリ
            p_ids = [pfm.id for pfm in performances.items]
            dc_target_stock_types = util.get_dc_target_stock_type_of_performances(
                self.context.session,
                p_ids,
                self.context.setting_id
            )

            # 「適用席種追加」フォーム
            form = DiscountCodeTargetStForm(
                organization_id=self.request.context.organization.id,
                discount_code_setting_id=self.context.setting_id
            )

            return {
                'setting': self.context.setting,
                'performances': performances,  # PythonのWebhelpersによるページネーション
                'dc_target_stock_types': dc_target_stock_types,  # Tabulatorによる一覧表示
                'form': form,
                'search_form': search_form
            }

        else:
            self.request.session.flash(u'検索条件に不備があります')
            return HTTPFound(
                self.request.route_path("discount_code.target_st_index", setting_id=self.context.setting.id,
                                        _query=self.request.GET))

    @view_config(route_name='discount_code.target_st_index',
                 request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/target_st/index.html')
    def target_st_index_post(self):
        form_type = self.request.POST.get('form_type')
        if form_type not in [DiscountCodeTargetStForm.FORM_REGISTER, DiscountCodeTargetStForm.FORM_DELETE]:
            self.request.session.flash(u'不適切な操作が行われました。再度実行し直してください。')
            return HTTPFound(
                self.request.route_path("discount_code.target_st_index", setting_id=self.context.setting_id,
                                        _query=self.request.GET))

        f = DiscountCodeTargetStForm(self.request.POST,
                                     organization_id=self.request.context.organization.id,
                                     discount_code_setting_id=self.context.setting_id
                                     )
        if not f.validate():
            self.request.session.flash(u'適用席種の登録に失敗しました。')
            for e in f.errors:
                for reason in f.errors.get(e):
                    self.request.session.flash(reason)

        else:
            if form_type == DiscountCodeTargetStForm.FORM_REGISTER:
                util.save_target_stock_type_data(
                    f.data['stock_type_id'],
                    self.context.setting_id,
                    f.data['event_id'],
                    f.data['performance_id']
                )

                self.request.session.flash(u'適用席種を登録しました。')

            elif form_type == DiscountCodeTargetStForm.FORM_DELETE:
                for t_id in f.data['id']:
                    DiscountCodeTargetStockType.get(id=t_id).delete()
                self.request.session.flash(u'適用席種を削除しました。')

        return HTTPFound(self.request.route_path("discount_code.target_st_index", setting_id=self.context.setting.id,
                                                 _query=self.request.GET))

    @view_config(route_name='discount_code.report_print')
    def report_print(self):
        t0 = time.time()
        codes = self.context.get_used_discount_order_by_setting_id()

        render_param = dict(codes=codes)
        r = render_to_response('altair.app.ticketing:templates/discount_code/report/export.txt', render_param,
                               request=self.request)
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = u"{}_report_{}.csv".format(get_safe_filename(self.context.setting.name), now)
        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', "attachment; filename*=utf-8''%s" % urllib.quote(filename.encode("utf-8")))
        ]
        logger.info("number of codes: {}, execution time {} sec".format(len(codes), str(time.time() - t0)))
        return Response(r.text.encode('cp932'), headers=headers)
