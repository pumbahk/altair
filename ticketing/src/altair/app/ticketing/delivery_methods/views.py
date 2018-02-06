# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from altair.app.ticketing.payments.plugins import QR_DELIVERY_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID, QR_AES_DELIVERY_PLUGIN_ID
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import DeliveryMethod
from altair.app.ticketing.delivery_methods.forms import DeliveryMethodForm
from altair.app.ticketing.core import models as c_models

@view_defaults(decorator=with_bootstrap, permission='master_editor')
class DeliveryMethods(BaseView):

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
            'form':DeliveryMethodForm(),
            'delivery_methods':delivery_methods,
        }

    @view_config(route_name='delivery_methods.new', request_method='GET', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def new(self):
        organization_setting = c_models.OrganizationSetting.filter_by(organization_id=self.context.user.organization_id).one()
        form = DeliveryMethodForm(organization_id=self.context.user.organization_id)
        return {
            'form': form,
            'i18n_org': organization_setting.i18n
        }

    @view_config(route_name='delivery_methods.new', request_method='POST', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def new_post(self):
        if long(self.request.POST.get('organization_id'), 0) != self.context.user.organization_id:
            self.request.session.flash(u'ユーザーを切り替えたため、引取方法の保存は失敗しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        f = DeliveryMethodForm(self.request.POST)
        organization_setting = c_models.OrganizationSetting.filter_by(organization_id=self.context.user.organization_id).one()
        if f.validate():
            delivery_method = merge_session_with_post(DeliveryMethod(), f.data, excludes={'single_qr_mode', 'expiration_date', 'allow_sp_qr_aes'})
            delivery_method.preferences.setdefault(unicode(QR_DELIVERY_PLUGIN_ID), {})['single_qr_mode'] = f.single_qr_mode.data
            delivery_method.preferences.setdefault(unicode(RESERVE_NUMBER_DELIVERY_PLUGIN_ID), {})['expiration_date'] = f.expiration_date.data
            delivery_method.preferences.setdefault(unicode(QR_AES_DELIVERY_PLUGIN_ID), {})['allow_sp_qr_aes'] = f.allow_sp_qr_aes.data
            if organization_setting.i18n:
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
                'i18n_org': organization_setting.i18n
            }

    @view_config(route_name='delivery_methods.edit', request_method='GET', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def edit(self):
        delivery_method_id = long(self.request.matchdict.get('delivery_method_id', 0))
        obj = DeliveryMethod.query.filter_by(id=delivery_method_id).one()
        form = DeliveryMethodForm(obj=obj)
        form.single_qr_mode.data = obj.preferences.get(unicode(QR_DELIVERY_PLUGIN_ID), {}).get('single_qr_mode', False)
        form.expiration_date.data = obj.preferences.get(unicode(RESERVE_NUMBER_DELIVERY_PLUGIN_ID), {}).get('expiration_date', None)
        form.allow_sp_qr_aes.data = obj.preferences.get(unicode(QR_AES_DELIVERY_PLUGIN_ID), {}).get('allow_sp_qr_aes', False)
        organization_setting = c_models.OrganizationSetting.filter_by(organization_id=self.context.user.organization_id).one()
        if organization_setting.i18n:
            form.name_en.data = obj.preferences.get(u'en', {}).get('name', u'')
            form.description_en.data = obj.preferences.get(u'en', {}).get('description', u'')
            form.name_zh_cn.data = obj.preferences.get(u'zh_CN', {}).get('name', u'')
            form.description_zh_cn.data = obj.preferences.get(u'zh_CN', {}).get('description', u'')
            form.name_zh_tw.data = obj.preferences.get(u'zh_TW', {}).get('name', u'')
            form.description_zh_tw.data = obj.preferences.get(u'zh_TW', {}).get('description', u'')
            form.name_ko.data = obj.preferences.get(u'ko', {}).get('name', u'')
            form.description_ko.data = obj.preferences.get(u'ko', {}).get('description', u'')
        return {
            'form': form,
            'i18n_org': organization_setting.i18n
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

        f = DeliveryMethodForm(self.request.POST)
        organization_setting = c_models.OrganizationSetting.filter_by(organization_id=self.context.user.organization_id).one()
        if f.validate():
            delivery_method = merge_session_with_post(delivery_method, f.data, excludes={'single_qr_mode', 'expiration_date'})
            delivery_method.preferences.setdefault(unicode(QR_DELIVERY_PLUGIN_ID), {})['single_qr_mode'] = f.single_qr_mode.data
            delivery_method.preferences.setdefault(unicode(RESERVE_NUMBER_DELIVERY_PLUGIN_ID), {})['expiration_date'] = f.expiration_date.data
            delivery_method.preferences.setdefault(unicode(QR_AES_DELIVERY_PLUGIN_ID), {})['allow_sp_qr_aes'] = f.allow_sp_qr_aes.data
            if organization_setting.i18n:
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
                'i18n_org': organization_setting.i18n
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

