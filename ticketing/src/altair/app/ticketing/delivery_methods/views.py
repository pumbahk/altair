# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_DELIVERY_PLUGIN_ID, WEB_COUPON_DELIVERY_PLUGIN_ID
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import DeliveryMethod


@view_defaults(decorator=with_bootstrap, permission='master_editor')
class DeliveryMethods(BaseView):

    EXPIRATION_DATE_PLUGIN_IDS = (RESERVE_NUMBER_DELIVERY_PLUGIN_ID, WEB_COUPON_DELIVERY_PLUGIN_ID)

    @view_config(route_name='delivery_methods.index', renderer='altair.app.ticketing:templates/delivery_methods/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'DeliveryMethod.display_order')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = DeliveryMethod.filter_by(organization_id=self.context.user.organization_id)
        query = query.order_by('DeliveryMethod.selectable desc') \
                     .order_by(sort + ' ' + direction)

        delivery_methods = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':self.context.form_maker.make_form(),
            'delivery_methods':delivery_methods,
        }

    @view_config(route_name='delivery_methods.new', request_method='GET', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def new(self):
        f = self.context.form_maker.make_form(organization_id=self.context.organization.id)

        return {
            'form': f,
            'i18n_org': self.context.organization.setting.i18n,
            'is_enable_skidata': self.context.organization.setting.enable_skidata
        }

    @view_config(route_name='delivery_methods.new', request_method='POST', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def new_post(self):
        if long(self.request.POST.get('organization_id'), 0) != self.context.organization.id:
            self.request.session.flash(u'ユーザーを切り替えたため、引取方法の保存は失敗しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        f = self.context.form_maker.make_form(self.request.POST)
        if f.validate():
            # カスタマイズフィールドはpreferencesで保存されるため、excludesにフィールドを入れる
            excludes = {'single_qr_mode', 'expiration_date', 'term_sales'}
            customized_fields = f.get_customized_fields()
            if customized_fields:
                excludes.update(customized_fields)

            delivery_method = merge_session_with_post(DeliveryMethod(), f.data, excludes=excludes)
            preferences = delivery_method.preferences
            # 相対有効期限を設定
            if delivery_method.delivery_plugin_id in self.EXPIRATION_DATE_PLUGIN_IDS:
                preferences.setdefault(str(delivery_method.delivery_plugin_id), {})['expiration_date'] = f.expiration_date.data

                # WEBクーポンのプラグインの場合に期間券を保存
                preferences.setdefault(str(delivery_method.delivery_plugin_id), {})[
                    'term_sales'] = f.term_sales.data

            # QR系の引取方法しかsingle_qr_modeを使わない。（Falseの可能性があり）
            if f.single_qr_mode.data is not None:
                delivery_method.preferences.setdefault(unicode(f.delivery_plugin_id.data), {})['single_qr_mode'] = f.single_qr_mode.data
            if f.sej_delivery_with_skidata.data is not None:
                delivery_method.preferences.setdefault(unicode(f.delivery_plugin_id.data), {})[
                    'sej_delivery_with_skidata'] = f.sej_delivery_with_skidata.data
            # カスタマイズフィールドの情報をpreferencesに入れる
            for field_name in customized_fields:
                delivery_method.preferences.setdefault(unicode(f.delivery_plugin_id.data), {})[field_name] = f[field_name].data

            if self.context.organization.setting.i18n:
                delivery_method.preferences.setdefault(u'en', {})['name'] = f.name_en.data
                delivery_method.preferences.setdefault(u'en', {})['description'] = f.description_en.data
                delivery_method.preferences.setdefault(u'zh_CN', {})['name'] = f.name_zh_cn.data
                delivery_method.preferences.setdefault(u'zh_CN', {})['description'] = f.description_zh_cn.data
                delivery_method.preferences.setdefault(u'zh_TW', {})['name'] = f.name_zh_tw.data
                delivery_method.preferences.setdefault(u'zh_TW', {})['description'] = f.description_zh_tw.data
                delivery_method.preferences.setdefault(u'ko', {})['name'] = f.name_ko.data
                delivery_method.preferences.setdefault(u'ko', {})['description'] = f.description_ko.data
            delivery_method.organization_id = self.context.user.organization_id
            delivery_method.save()

            self.request.session.flash(u'引取方法を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'i18n_org': self.context.organization.setting.i18n,
                'is_enable_skidata': self.context.organization.setting.enable_skidata
            }

    @view_config(route_name='delivery_methods.edit', request_method='GET', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def edit(self):
        delivery_method_id = long(self.request.matchdict.get('delivery_method_id', 0))
        obj = DeliveryMethod.query.filter_by(id=delivery_method_id).one()
        f = self.context.form_maker.make_form(obj=obj)

        f.expiration_date.data = obj.preferences.get(unicode(obj.delivery_plugin_id), {}).get('expiration_date', None)
        f.term_sales.data = obj.preferences.get(unicode(obj.delivery_plugin_id), {}).get('term_sales', None)
        # QR系の引取方法しかsingle_qr_modeを使わない。
        f.single_qr_mode.data = obj.preferences.get(unicode(obj.delivery_plugin_id), {}).get('single_qr_mode', False)
        f.sej_delivery_with_skidata.data = obj.preferences.get(unicode(obj.delivery_plugin_id), {}).get(
            'sej_delivery_with_skidata', False)
        # preferencesからカスタマイズフィールドの情報を取得（カスタマイズフィールドはdelivery_plugin_idに絞ってる）
        customized_fields = f.get_customized_fields()
        for field_name in customized_fields:
            f._fields[field_name].data = obj.preferences.get(unicode(obj.delivery_plugin_id), {}).get(field_name, None)

        if self.context.organization.setting.i18n:
            f.name_en.data = obj.preferences.get(u'en', {}).get('name', u'')
            f.description_en.data = obj.preferences.get(u'en', {}).get('description', u'')
            f.name_zh_cn.data = obj.preferences.get(u'zh_CN', {}).get('name', u'')
            f.description_zh_cn.data = obj.preferences.get(u'zh_CN', {}).get('description', u'')
            f.name_zh_tw.data = obj.preferences.get(u'zh_TW', {}).get('name', u'')
            f.description_zh_tw.data = obj.preferences.get(u'zh_TW', {}).get('description', u'')
            f.name_ko.data = obj.preferences.get(u'ko', {}).get('name', u'')
            f.description_ko.data = obj.preferences.get(u'ko', {}).get('description', u'')
        return {
            'form': f,
            'i18n_org': self.context.organization.setting.i18n,
            'is_enable_skidata': self.context.organization.setting.enable_skidata
            }

    @view_config(route_name='delivery_methods.edit', request_method='POST', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def edit_post(self):
        delivery_method_id = int(self.request.matchdict.get('delivery_method_id', 0))
        delivery_method = DeliveryMethod.get(delivery_method_id)
        if delivery_method is None:
            return HTTPNotFound('delivery_method id %d is not found' % delivery_method_id)
        if delivery_method.organization_id != self.context.user.organization_id:
            self.request.session.flash(u'ユーザーを切り替えたため、引取方法の保存は失敗しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

        f = self.context.form_maker.make_form(self.request.POST)

        if f.validate():
            # カスタマイズフィールドはpreferencesで保存されるため、excludesにフィールドを入れる
            excludes = {'single_qr_mode', 'expiration_date', 'term_sales', 'sej_ticket_with_skidata'}
            get_customized_fields = getattr(f, 'get_customized_fields', None)
            customized_fields = get_customized_fields() if get_customized_fields else []
            if customized_fields:
                excludes.update(customized_fields)

            delivery_method = merge_session_with_post(delivery_method, f.data, excludes=excludes)
            preferences = delivery_method.preferences
            # 配送プラグインが変わる場合に元のプラグインの相対有効期限と期間券が残らないように先に削除しておく
            for plugin_id_ in self.EXPIRATION_DATE_PLUGIN_IDS:
                delivery_plugin_setting = preferences.get(unicode(plugin_id_), None)
                if delivery_plugin_setting:
                    delivery_plugin_setting.pop('expiration_date', None)
                    delivery_plugin_setting.pop('term_sales', None)
            # 相対有効期限と期間券を設定
            if delivery_method.delivery_plugin_id in self.EXPIRATION_DATE_PLUGIN_IDS:
                preferences.setdefault(unicode(delivery_method.delivery_plugin_id), {})[
                    'expiration_date'] = f.expiration_date.data
                preferences.setdefault(unicode(delivery_method.delivery_plugin_id), {})[
                    'term_sales'] = f.term_sales.data

            # QR系の引取方法しかsingle_qr_modeを使わない。（Falseの可能性があり）
            if f.single_qr_mode.data is not None:
                delivery_method.preferences.setdefault(unicode(f.delivery_plugin_id.data), {})['single_qr_mode'] = f.single_qr_mode.data
            if f.sej_delivery_with_skidata.data is not None:
                delivery_method.preferences.setdefault(unicode(f.delivery_plugin_id.data), {})[
                    'sej_delivery_with_skidata'] = f.sej_delivery_with_skidata.data
            # カスタマイズフィールドの情報をpreferencesに入れる
            for field_name in customized_fields:
                delivery_method.preferences.setdefault(unicode(f.delivery_plugin_id.data), {})[field_name] = f[field_name].data

            if self.context.organization.setting.i18n:
                delivery_method.preferences.setdefault(u'en', {})['name'] = f.name_en.data
                delivery_method.preferences.setdefault(u'en', {})['description'] = f.description_en.data
                delivery_method.preferences.setdefault(u'zh_CN', {})['name'] = f.name_zh_cn.data
                delivery_method.preferences.setdefault(u'zh_CN', {})['description'] = f.description_zh_cn.data
                delivery_method.preferences.setdefault(u'zh_TW', {})['name'] = f.name_zh_tw.data
                delivery_method.preferences.setdefault(u'zh_TW', {})['description'] = f.description_zh_tw.data
                delivery_method.preferences.setdefault(u'ko', {})['name'] = f.name_ko.data
                delivery_method.preferences.setdefault(u'ko', {})['description'] = f.description_ko.data
            delivery_method.organization_id = self.context.user.organization_id
            delivery_method.save()

            self.request.session.flash(u'引取方法を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'i18n_org': self.context.organization.setting.i18n,
                'is_enable_skidata': self.context.organization.setting.enable_skidata
            }

    @view_config(route_name='delivery_methods.delete')
    def delete(self):
        delivery_method_id = int(self.request.matchdict.get('delivery_method_id', 0))
        delivery_method = DeliveryMethod.get(delivery_method_id)
        if delivery_method is None:
            return HTTPNotFound('delivery_method id %d is not found' % delivery_method_id)

        location = route_path('delivery_methods.index', self.request)
        try:
            delivery_method.delete()
            self.request.session.flash(u'引取方法を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

