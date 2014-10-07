# encoding: utf-8

import json
import logging
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from webob.multidict import MultiDict

from datetime import datetime

from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.views import BaseView
from altair.sqla import get_relationship_query
from ..core.models import Product
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.users.models import UserPointAccount
from .models import PointGrantSetting, PointGrantHistoryEntry
from .forms import PointGrantSettingForm, PointGrantHistoryEntryForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class PointGrantSettings(BaseView):
    @view_config(route_name='point_grant_settings.index', renderer='altair.app.ticketing:templates/point_grant_settings/index.html', permission='event_viewer')
    def index(self):
        query = get_relationship_query(self.context.user.organization.point_grant_settings)
        return {
            'point_grant_settings': paginate.Page(
                query,
                page=int(self.request.params.get('page', 0)),
                items_per_page=20,
                url=paginate.PageURL_WebOb(self.request),
                item_count=query.count()
                ),
            'organization_setting': self.context.user.organization.setting,
            }

    @view_config(route_name='point_grant_settings.show', request_method='GET', renderer='altair.app.ticketing:templates/point_grant_settings/show.html')
    def show(self):
        return { 'point_grant_setting': self.context.point_grant_setting }

    @view_config(route_name='point_grant_settings.new', request_method='GET', renderer='altair.app.ticketing:templates/point_grant_settings/edit.html', xhr=False)
    @view_config(route_name='point_grant_settings.new', request_method='GET', renderer='altair.app.ticketing:templates/point_grant_settings/_form.html', xhr=True)
    def new(self):
        return {
            'form': PointGrantSettingForm(context=self.context),
            }

    @view_config(route_name='point_grant_settings.new', request_method='POST', renderer='altair.app.ticketing:templates/point_grant_settings/edit.html', xhr=False)
    def new_post(self):
        form = PointGrantSettingForm(self.request.POST, context=self.context)
        if not form.validate():
            return {
                'form': form
                }
        obj = PointGrantSetting(
            organization_id=self.context.user.organization_id,
            name=form.name.data,
            type=form.type.data,
            fixed=form.fixed.data,
            rate=form.rate.data,
            start_at=form.start_at.data,
            end_at=form.end_at.data
            )
        obj.save()
        self.request.session.flash(u'ポイント付与設定を保存しました')
        return HTTPFound(self.request.route_path('point_grant_settings.index'))

    @view_config(route_name='point_grant_settings.new', request_method='POST', renderer='altair.app.ticketing:templates/point_grant_settings/_form.html', xhr=True)
    def new_post_xhr(self):
        form = PointGrantSettingForm(self.request.POST, context=self.context)
        if not form.validate():
            return {
                'form': form
                }
        obj = PointGrantSetting(
            organization_id=self.context.user.organization_id,
            name=form.name.data,
            type=form.type.data,
            fixed=form.fixed.data,
            rate=form.rate.data,
            start_at=form.start_at.data,
            end_at=form.end_at.data
            )
        obj.save()
        self.request.session.flash(u'ポイント付与設定を保存しました')
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='point_grant_settings.edit', request_method='GET', renderer='altair.app.ticketing:templates/point_grant_settings/edit.html', xhr=False)
    @view_config(route_name='point_grant_settings.edit', request_method='GET', renderer='altair.app.ticketing:templates/point_grant_settings/_form.html', xhr=True)
    def edit(self):
        return {
            'form': PointGrantSettingForm(obj=self.context.point_grant_setting, context=self.context),
            }

    def _edit_post(self):
        form = PointGrantSettingForm(formdata=self.request.POST, context=self.context)
        if not form.validate():
            return form

        obj = self.context.point_grant_setting
        obj.organization_id = self.context.user.organization_id
        obj.name = form.name.data
        obj.type = form.type.data
        obj.fixed = form.fixed.data
        obj.rate = form.rate.data
        obj.start_at = form.start_at.data
        obj.end_at = form.end_at.data
        obj.save()
        return None

    @view_config(route_name='point_grant_settings.edit', request_method='POST', renderer='altair.app.ticketing:templates/point_grant_settings/edit.html', xhr=False)
    def edit_post(self):
        form = self._edit_post()
        if form:
            return { 'form': form }
        return HTTPFound(location=self.request.route_path('point_grant_settings.index'))

    @view_config(route_name='point_grant_settings.edit', request_method='POST', renderer='altair.app.ticketing:templates/point_grant_settings/_form.html', xhr=True)
    def edit_post_xhr(self):
        form = self._edit_post()
        if form:
            return { 'form': form }
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='point_grant_settings.delete_confirm', renderer='altair.app.ticketing:templates/point_grant_settings/_delete_confirm.html', xhr=True)
    def delete_confirm(self):
        point_grant_setting_ids = [long(id) for id in self.request.POST.getall('point_grant_setting_id')]
        return dict(point_grant_settings=PointGrantSetting.query.filter(PointGrantSetting.id.in_(point_grant_setting_ids)))

    @view_config(route_name='point_grant_settings.delete', renderer='altair.app.ticketing:templates/refresh.html', xhr=True)
    def delete(self):
        point_grant_setting_ids = [long(id) for id in self.request.POST.getall('point_grant_setting_id')]
        PointGrantSetting.query.filter(PointGrantSetting.id.in_(point_grant_setting_ids)).update(dict(deleted_at=datetime.now()), synchronize_session=False)
        return {}

    @view_config(route_name='point_grant_settings.products.remove', request_method='POST', renderer='altair.app.ticketing:templates/refresh.html')
    def remove_product(self):
        product_ids = [long(id) for id in self.request.POST.getall('product_id')]
        self.context.point_grant_setting.target_products.difference_update(Product.query.filter(Product.id.in_(product_ids)))
        return HTTPFound(location=self.request.route_path('point_grant_settings.show', point_grant_setting_id=self.context.point_grant_setting.id))

    @view_config(route_name='point_grant_history_entry.new', request_method='GET', renderer='altair.app.ticketing:templates/loyalty/point_grant_history_entry_form.html', xhr=True, permission="event_editor")
    def new_xhr_point_grant_history_entry(self):
        form = PointGrantHistoryEntryForm(context=self.context, new_form=True)
        return {'form': form, 'action': self.request.current_route_path(_query=dict(order_id=self.context.order_id))}

    @view_config(route_name='point_grant_history_entry.edit', request_method='GET', renderer='altair.app.ticketing:templates/loyalty/point_grant_history_entry_form.html', xhr=True, permission="event_editor")
    def edit_xhr_point_grant_history_entry(self):
        form = PointGrantHistoryEntryForm(obj=self.context.point_grant_history_entry, context=self.context)
        return {'form': form, 'action': self.request.path}

    @view_config(route_name='point_grant_history_entry.new', request_method='POST', renderer='altair.app.ticketing:templates/loyalty/point_grant_history_entry_form.html', xhr=True, permission="event_editor")
    def new_post(self):
        form = PointGrantHistoryEntryForm(formdata=self.request.POST, context=self.context, new_form=True)
        if form.validate():
            order_id = long(self.context.order_id)
            try:
                user_point_account_id = UserPointAccount.query.join(Order, UserPointAccount.user_id == Order.user_id).filter(Order.id == order_id).first().id
                submitted_on=form.submitted_on.data
                amount=float(form.amount.data)
                operator_id = self.context.user.id
                point_grant_history_entry = \
                    PointGrantHistoryEntry(user_point_account_id=user_point_account_id, order_id=order_id, submitted_on=submitted_on, amount=amount, edited_by=operator_id , manual_grant=True)
                point_grant_history_entry.add()
                self.request.session.flash(u'ポイント付与エントリを保存しました。')
                return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
            except Exception, exception:
                self.request.session.flash(exception.message)
                raise HTTPFound(location=self.request.route_path('orders.show', order_id=order_id))
        else:
            return {'form': form, 'action': self.request.path}

    @view_config(route_name="point_grant_history_entry.edit", request_method="POST", renderer='altair.app.ticketing:templates/loyalty/point_grant_history_entry_form.html', xhr=True, permission="event_editor")
    def update_point_grant_history_entry(self):
        form = PointGrantHistoryEntryForm(formdata=self.request.POST, context=self.context)
        if form.validate():
            point_grant_history_entry = self.context.point_grant_history_entry
            try:
                point_grant_history_entry.edited_by = self.context.user.id
                point_grant_history_entry.submitted_on = form.submitted_on.data
                point_grant_history_entry.amount=form.amount.data
                point_grant_history_entry.manual_grant=True

                DBSession.add(point_grant_history_entry)
                DBSession.flush()
                self.request.session.flash(u'ポイント付与エントリを保存しました。')
                return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
            except Exception, exception:
                self.request.session.flash(exception.message)
                raise HTTPFound(location=self.request.route_path('orders.show', self.request, order_id=point_grant_history_entry.order_id))
        else:
            return {'form': form, 'action': self.request.path}

    @view_config(route_name="point_grant_history_entry.delete", request_method="POST", permission="event_editor")
    def delete_point_grant_history_entry(self):
        try:
            self.context.point_grant_history_entry.delete()
            self.request.session.flash(u'ポイント付与エントリを削除しました。')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        except Exception, exception:
            self.request.session.flash(exception.message)
            raise HTTPFound(location=self.request.route_path('orders.show', order_id=self.context.point_grant_history_entry.order_id))


