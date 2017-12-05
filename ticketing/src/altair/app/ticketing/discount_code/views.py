# encoding: utf-8

import logging

import webhelpers.paginate as paginate
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.views import BaseView
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config, view_defaults
from .api import is_enabled_discount_code_checked
from .forms import DiscountCodeSettingForm
from .models import DiscountCodeSetting, delete_discount_code_setting

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap,
               permission='event_editor',
               custom_predicates=(is_enabled_discount_code_checked,))
class DiscountCodeSettings(BaseView):
    @view_config(route_name='discount_code_settings.index',
                 renderer='altair.app.ticketing:templates/discount_code/settings/index.html', permission='event_viewer')
    def index(self):
        sort = self.request.GET.get('sort', 'DiscountCodeSetting.end_at')
        direction = self.request.GET.get('direction', 'desc')

        query = DiscountCodeSetting.query.filter_by(organization_id=self.context.user.organization_id)
        query = query.order_by(sort + ' ' + direction) \
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

    @view_config(route_name='discount_code_settings.new', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/settings/_form.html', xhr=True)
    def new(self):
        f = DiscountCodeSettingForm()
        return {
            'form': f,
            'action': self.request.path,
        }

    @view_config(route_name='discount_code_settings.new', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/settings/_form.html', xhr=True)
    def new_post(self):
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

    @view_config(route_name='discount_code_settings.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/discount_code/settings/_form.html', xhr=True)
    def edit(self):
        setting_id = int(self.request.matchdict.get('setting_id', 0))
        setting = DiscountCodeSetting.query.filter_by(id=setting_id).filter_by(
            organization_id=self.context.user.organization_id).first()
        if setting is None:
            return HTTPNotFound('setting id %d is not found' % setting_id)

        f = DiscountCodeSettingForm(obj=setting)
        return {
            'form': f,
            'action': self.request.path,
        }

    @view_config(route_name='discount_code_settings.edit', request_method='POST',
                 renderer='altair.app.ticketing:templates/discount_code/settings/_form.html', xhr=True)
    def edit_post(self):
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

    @view_config(route_name='discount_code_settings.delete')
    def delete(self):
        location = self.request.route_path('discount_code_settings.index')
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
