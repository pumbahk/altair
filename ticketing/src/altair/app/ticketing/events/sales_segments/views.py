# -*- coding: utf-8 -*-

import json
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, Performance, SalesSegment, SalesSegmentGroup, Product, PaymentDeliveryMethodPair, Organization
from altair.app.ticketing.events.payment_delivery_method_pairs.forms import PaymentDeliveryMethodPairForm
from .forms import SalesSegmentForm, PointGrantSettingAssociationForm, EditSalesSegmentForm
from altair.app.ticketing.memberships.forms import MemberGroupForm
from altair.app.ticketing.users.models import MemberGroup, Membership
from altair.app.ticketing.loyalty.models import PointGrantSetting
from webob.multidict import MultiDict
from .resources import SalesSegmentEditor
from datetime import datetime

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class SalesSegments(BaseView):
    def _pdmp_map(self, sales_segment_groups):
        """ 販売区分グループごとのPDMP json
        """
        mapped = {}
        for ssg in sales_segment_groups:
            mapped[str(ssg.id)] = [(pdmp.id, pdmp.payment_method.name + " - " + pdmp.delivery_method.name) 
                              for pdmp in ssg.payment_delivery_method_pairs]
        return json.dumps(mapped)

    def _account_map(self, sales_segment_groups):
        """ 販売区分グループごとのAccount json
        """
        mapped = {}
        for ssg in sales_segment_groups:
            mapped[str(ssg.id)] = ssg.account_id
        return json.dumps(mapped)

    @property
    def sales_segment_groups(self):
        performance = self.context.performance
        if performance is None:
            return []

        return performance.event.sales_segment_groups

    @view_config(route_name='sales_segments.index', renderer='altair.app.ticketing:templates/sales_segments/index.html', permission='event_viewer')
    def index(self):
        event_id = long(self.request.matchdict.get('event_id', 0))
        event = Event.query.filter_by(id=event_id, organization_id=self.context.user.organization_id).one()
        performance_id = self.request.params.get('performance_id')
        if performance_id is not None:
            performance_id = long(performance_id)
            performance = Performance.query.filter_by(id=performance_id, event_id=event_id).one()
        else:
            performance = None

        sort = self.request.GET.get('sort', 'SalesSegment.start_at')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = SalesSegment.query \
            .join(SalesSegment.sales_segment_group) \
            .join(SalesSegmentGroup.event) \
            .filter(Organization.id == self.context.user.organization_id)
        if event is not None:
            query = query.filter(SalesSegmentGroup.event_id==event.id)
        if performance is not None:
            query = query.filter(SalesSegment.performance_id==performance.id)
        query = query.order_by(sort + ' ' + direction)

        sales_segments = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'event': event,
            'performance': performance,
            'sales_segments':sales_segments,
        }

    @view_config(route_name='sales_segments.show', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/show.html')
    def show(self):
        if self.context.sales_segment is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'販売区分が存在しません',
            }))

        return {
            'sales_segment': self.context.sales_segment,
            'form_pdmp':PaymentDeliveryMethodPairForm(),
            }

    @view_config(route_name='sales_segments.new', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/edit.html', xhr=False)
    def new(self):
        return {
            'event': self.context.event,
            'performance': self.context.performance,
            'sales_segment_group': self.context.sales_segment_group,
            'form': SalesSegmentForm(context=self.context),
            'action': self.request.path,
            'pdmp_map': self._pdmp_map(self.sales_segment_groups),
            'account_map':self._account_map(self.sales_segment_groups)
            }

    @view_config(route_name='sales_segments.new', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    def new_xhr(self):
        return {
            'form': SalesSegmentForm(context=self.context),
            'action': self.request.path,
            'pdmp_map': self._pdmp_map(self.sales_segment_groups),
            'account_map':self._account_map(self.sales_segment_groups)
            }

    @view_config(route_name='sales_segments.new', request_method='POST', renderer='altair.app.ticketing:templates/sales_segments/edit.html', xhr=False)
    def new_post(self):
        f = SalesSegmentForm(self.request.POST, context=self.context)

        if f.validate():
            if f.start_at.data is None:
                f.start_at.data = datetime.now()
            if f.end_at.data is None:
                f.end_at.data = datetime.now()
            sales_segment_group_id = f.sales_segment_group_id.data
            sales_segment_group = SalesSegmentGroup.query.filter_by(id=sales_segment_group_id).one()
            sales_segment = sales_segment_group.new_sales_segment()
            sales_segment = merge_session_with_post(sales_segment, f.data)

            pdmps = [pdmp
                     for pdmp in sales_segment_group.payment_delivery_method_pairs
                     if pdmp.id in f.payment_delivery_method_pairs.data]

            sales_segment.payment_delivery_method_pairs = pdmps
            sales_segment.save()

            self.request.session.flash(u'販売区分を作成しました')
            return HTTPFound(self.request.route_path(
                'sales_segments.index',
                event_id=sales_segment.sales_segment_group.event_id,
                sales_segment_group_id=sales_segment.sales_segment_group_id,
                _query={'performance_id': sales_segment.performance_id}))
        else:
            return {
                'event': self.context.event,
                'performance': self.context.performance,
                'sales_segment_group': self.context.sales_segment_group,
                'form': f,
                'action': self.request.path_url,
                'pdmp_map': self._pdmp_map(self.sales_segment_groups),
                'account_map':self._account_map(self.sales_segment_groups)
                }

    @view_config(route_name='sales_segments.new', request_method='POST', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    def new_post_xhr(self):
        f = SalesSegmentForm(self.request.POST, context=self.context)

        if f.validate():
            if f.start_at.data is None:
                f.start_at.data = datetime.now()
            if f.end_at.data is None:
                f.end_at.data = datetime.now()
            sales_segment_group_id = f.sales_segment_group_id.data
            sales_segment_group = SalesSegmentGroup.query.filter_by(id=sales_segment_group_id).one()
            sales_segment = sales_segment_group.new_sales_segment()
            sales_segment = merge_session_with_post(sales_segment, f.data)

            pdmps = [pdmp
                     for pdmp in sales_segment_group.payment_delivery_method_pairs
                     if pdmp.id in f.payment_delivery_method_pairs.data]
            sales_segment.payment_delivery_method_pairs = pdmps
            sales_segment.save()

            self.request.session.flash(u'販売区分を作成しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'action': self.request.path_url,
                'pdmp_map': self._pdmp_map(self.sales_segment_groups),
                'account_map':self._account_map(self.sales_segment_groups)
                }

    #@view_config(route_name='sales_segments.edit', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/edit.html', xhr=False)
    def edit(self):
        return {
            'event': self.context.sales_segment.sales_segment_group.event,
            'performance': self.context.sales_segment.performance,
            'sales_segment_group': self.context.sales_segment.sales_segment_group,
            'sales_segment': self.context.sales_segment,
            'form': SalesSegmentForm(obj=self.context.sales_segment, context=self.context),
            'action': self.request.path,
            'pdmp_map': self._pdmp_map(self.sales_segment_groups),
            'account_map':self._account_map(self.sales_segment_groups)
            }

    #@view_config(route_name='sales_segments.edit', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    def edit_xhr(self):
        return {
            'form': SalesSegmentForm(obj=self.context.sales_segment, context=self.context),
            'action': self.request.path,
            'pdmp_map': self._pdmp_map(self.sales_segment_groups),
            'account_map':self._account_map(self.sales_segment_groups)
            }

    def _edit_post(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'販売区分が存在しません',
            }))

        f = SalesSegmentForm(self.request.POST, context=self.context)
        if not f.validate():
            return f
        pdmp_ids = self.request.params.getall('payment_delivery_method_pairs[]')

        pdmps = list(PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id.in_(pdmp_ids)).filter(PaymentDeliveryMethodPair.sales_segment_group_id==sales_segment.sales_segment_group_id))
        
        if self.request.matched_route.name == 'sales_segments.copy':
            with_pdmp = bool(f.copy_payment_delivery_method_pairs.data)
            id_map = SalesSegment.create_from_template(sales_segment, with_payment_delivery_method_pairs=with_pdmp)
            f.id.data = id_map[sales_segment_id]
            new_sales_segment = merge_session_with_post(SalesSegment.get(f.id.data), f.data)
            new_sales_segment.save()
            if f.copy_products.data:
                for product in sales_segment.product:
                    Product.create_from_template(template=product, with_product_items=True, stock_holder_id=f.copy_to_stock_holder.data, sales_segment=id_map)
        else:
            sales_segment = merge_session_with_post(sales_segment, f.data)
            sales_segment.payment_delivery_method_pairs = pdmps
            sales_segment.save()

        self.request.session.flash(u'販売区分を保存しました')
        return None

    #@view_config(route_name='sales_segments.edit', request_method='POST', renderer='altair.app.ticketing:templates/sales_segments/edit.html', xhr=False)
    def edit_post(self):
        f = self._edit_post()
        if f is None:
            return HTTPFound(location=self.request.route_path('sales_segments.edit', sales_segment_id=self.context.sales_segment.id))
        else:
            return {
                'event': self.context.event,
                'performance': self.context.performance,
                'sales_segment_group': self.context.sales_segment_group,
                'sales_segment': self.context.sales_segment,
                'form':f,
                'action': self.request.path_url,
                'pdmp_map': self._pdmp_map(self.sales_segment_groups),
                'account_map':self._account_map(self.sales_segment_groups)
                }

    #@view_config(route_name='sales_segments.edit', request_method='POST', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    def edit_post_xhr(self):
        f = self._edit_post()
        if f is None:
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'action': self.request.path_url,
                'pdmp_map': self._pdmp_map(self.sales_segment_groups),
                'account_map':self._account_map(self.sales_segment_groups)
                }

    @view_config(route_name='sales_segments.delete')
    def delete(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'販売区分が存在しません',
            }))

        location = route_path('sales_segment_groups.show', self.request, sales_segment_group_id=sales_segment.sales_segment_group_id)
        try:
            sales_segment.delete()
            self.request.session.flash(u'販売区分を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

    @view_config(renderer='json', route_name='sales_segments.api.get_payment_delivery_method_pairs')
    def get_payment_delivery_method_pairs(self):
        sales_segment_group_id = int(self.request.params.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id)
        result = [dict(pk=pdmp.id, name='%s - %s' % (pdmp.payment_method.name, pdmp.delivery_method.name)) for pdmp in sales_segment_group.payment_delivery_method_pairs]
        return {"result": result, "status": True}


@view_defaults(renderer='altair.app.ticketing:templates/sales_segments/edit.html',
               route_name='sales_segments.edit')
class EditSalesSegment(BaseView):
    @property
    def sales_segment(self):
        return self.context.sales_segment

    @property
    def sales_segment_group(self):
        return self.context.sales_segment.sales_segment_group

    @property
    def event(self):
        return self.context.sales_segment.sales_segment.event

    @property
    def account_choices(self):
        return [(a.id, a.name)
                for a
                in self.context.user.organization.accounts]

    @property
    def payment_delivery_method_pair_choices(self):
        return [(unicode(pdmp.id),
                 u'%s - %s' % (pdmp.payment_method.name, pdmp.delivery_method.name))
                for pdmp in self.context.sales_segment.sales_segment_group.payment_delivery_method_pairs
        ]


    @view_config()
    def __call__(self):
        form = EditSalesSegmentForm(obj=self.sales_segment,
                                    formdata=self.request.POST)
        form.account_id.choices = self.account_choices
        form.payment_delivery_method_pairs.choices = self.payment_delivery_method_pair_choices
        if self.request.method == "POST":
            if form.validate():
                editor = SalesSegmentEditor(self.sales_segment_group, form)
                editor.apply_changes(self.sales_segment)
                return None
        return dict(form=form)

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class SalesSegmentPointGrantSettings(BaseView):
    @view_config(route_name='sales_segments.point_grant_settings.add', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/_form_modal_point_grant_setting.html', xhr=True)
    def point_grant_settings_add(self):
        return {
            'form': PointGrantSettingAssociationForm(context=self.context),
            'action': self.request.path
            }

    @view_config(route_name='sales_segments.point_grant_settings.add', request_method='POST', renderer='altair.app.ticketing:templates/sales_segments/_form_modal_point_grant_setting.html', xhr=True)
    def point_grant_settings_add(self):
        form = PointGrantSettingAssociationForm(formdata=self.request.POST, context=self.context)
        if not form.validate():
            return {
                'form': PointGrantSettingAssociationForm(context=self.context),
                'action': self.request.path
                }
        self.context.sales_segment.point_grant_settings.append(PointGrantSetting.query.filter_by(id=form.point_grant_setting_id.data).one())
        return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='sales_segments.point_grant_settings.remove', request_method='POST', renderer='altair.app.ticketing:templates/refresh.html')
    def point_grant_settings_remove(self):
        from pyramid.request import Response
        point_grant_setting_ids = set(long(v) for v in self.request.POST.getall('point_grant_setting_id'))

        for point_grant_setting in PointGrantSetting.query.filter(PointGrantSetting.id.in_(point_grant_setting_ids)):
            import sys
            print >>sys.stderr, point_grant_setting
            self.context.sales_segment.point_grant_settings.remove(point_grant_setting)
        return_to = self.request.params.get('return_to')
        if return_to is None:
            return_to = self.request.route_path('sales_segments.show', event_id=self.context.event.id, sales_segment_id=self.context.sales_segment.id)
        return HTTPFound(location=return_to)
