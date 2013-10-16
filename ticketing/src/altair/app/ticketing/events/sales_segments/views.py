# -*- coding: utf-8 -*-
import logging
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
from .forms import SalesSegmentForm, PointGrantSettingAssociationForm
from altair.app.ticketing.memberships.forms import MemberGroupForm
from altair.app.ticketing.users.models import MemberGroup, Membership
from altair.app.ticketing.loyalty.models import PointGrantSetting
from webob.multidict import MultiDict
from .resources import SalesSegmentEditor
from datetime import datetime
from altair.pyramid_tz.api import get_timezone
from altair.app.ticketing.utils import toutc

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class SalesSegments(BaseView):
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


    @property
    def new_url(self):
        query = {}
        if self.context.performance:
            query['performance_id'] = self.context.performance.id
        if self.context.sales_segment_group:
            query['sales_segment_group_id'] = self.context.sales_segment_group.id
        return self.request.current_route_path(_query=query)

    @view_config(route_name='sales_segments.new', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    def new_get(self):
        return {
            'form': SalesSegmentForm(context=self.context),
            'action': self.new_url
            }

    @view_config(route_name='sales_segments.new', request_method='POST', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    def new_post(self):
        f = SalesSegmentForm(self.request.POST, context=self.context)
        if not f.validate():
            return {
                'form': f,
                'action': self.new_url
            }

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

    @view_config(route_name='sales_segments.delete')
    def delete(self):
        location = route_path('sales_segment_groups.show', self.request, sales_segment_group_id=self.context.sales_segment.sales_segment_group_id)
        try:
            self.context.sales_segment.delete()
            self.request.session.flash(u'販売区分を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

    @view_config(renderer='json', route_name='sales_segments.api.get_sales_segment_group_info')
    def get_sales_segment_group_info(self):
        sales_segment_group_id = None
        sales_segment_group = None
        performance_id = None
        performance = None
        try:
            sales_segment_group_id = long(self.request.matchdict['sales_segment_group_id'])
        except (ValueError, TypeError):
            pass
        if sales_segment_group_id:
            sales_segment_group = SalesSegmentGroup.query.filter_by(id=sales_segment_group_id).one()

        try:
            performance_id = long(self.request.params.get('performance_id'))
        except (ValueError, TypeError):
            pass
        if performance_id:
            performance = Performance.query.filter_by(id=performance_id).one()

        def stringize(x):
            if x is None:
                return None
            else:
                return unicode(x)
        tz = get_timezone(self.request)
        if performance:
            calculated_start_at = sales_segment_group.start_for_performance(performance)
            calculated_end_at = sales_segment_group.end_for_performance(performance)
        else:
            calculated_start_at = sales_segment_group.start_at
            calculated_end_at = sales_segment_group.end_at

        result = {
            'id': sales_segment_group.id,
            'event_id': sales_segment_group.event_id,
            'name': sales_segment_group.name,
            'kind': sales_segment_group.kind,
            'start_at': toutc(sales_segment_group.start_at, tz).isoformat() if sales_segment_group.start_at else None,
            'calculated_start_at': toutc(calculated_start_at, tz).isoformat() if calculated_start_at else None,
            'start_day_prior_to_performance': sales_segment_group.start_day_prior_to_performance,
            'start_time': sales_segment_group.start_time.strftime('%H:%M:%S') if sales_segment_group.start_time else None,
            'end_at': toutc(sales_segment_group.end_at, tz).isoformat() if sales_segment_group.end_at else None,
            'calculated_end_at': toutc(calculated_end_at, tz).isoformat() if calculated_end_at else None,
            'end_day_prior_to_performance': sales_segment_group.end_day_prior_to_performance,
            'end_time': sales_segment_group.end_time.strftime('%H:%M:%S') if sales_segment_group.end_time else None,
            'upper_limit': sales_segment_group.upper_limit,
            'order_limit': sales_segment_group.order_limit,
            'seat_choice': sales_segment_group.seat_choice,
            'public': sales_segment_group.public,
            'reporting': sales_segment_group.reporting,
            'margin_ratio': stringize(sales_segment_group.margin_ratio),
            'refund_ratio': stringize(sales_segment_group.refund_ratio),
            'printing_fee': stringize(sales_segment_group.printing_fee),
            'registration_fee': stringize(sales_segment_group.registration_fee),
            'auth3d_notice': sales_segment_group.auth3d_notice,
            'payment_delivery_method_pairs': [
                (pdmp.id, pdmp.payment_method.name + " - " + pdmp.delivery_method.name) 
                for pdmp in sales_segment_group.payment_delivery_method_pairs
                ],
            'account_id': sales_segment_group.account_id,
            }
        return {"result": result, "status": 'ok'}


@view_defaults(decorator=with_bootstrap, permission='event_editor')
class EditSalesSegment(BaseView):

    def _render_params(self, form):
        return dict(
            form=form,
            event=self.context.event,
            performance=self.context.performance,
            sales_segment=self.context.sales_segment,
            action=self.request.route_path(self.request.matched_route.name, **self.request.matchdict)
        )

    @view_config(route_name='sales_segments.copy', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    @view_config(route_name='sales_segments.edit', request_method='GET', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    def get(self):
        form = SalesSegmentForm(obj=self.context.sales_segment, formdata=self.request.GET, context=self.context)
        form.payment_delivery_method_pairs.data = [pdmp.id for pdmp in self.context.sales_segment.payment_delivery_method_pairs]
        return self._render_params(form)

    @view_config(route_name='sales_segments.copy', request_method='POST', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    @view_config(route_name='sales_segments.edit', request_method='POST', renderer='altair.app.ticketing:templates/sales_segments/_form.html', xhr=True)
    def post(self):
        form = SalesSegmentForm(obj=self.context.sales_segment, formdata=self.request.POST, context=self.context)
        if 'lot_id' in self.request.POST:
            form.performance_id.choices = [(None, None)]
        if form.validate():
            editor = SalesSegmentEditor(self.context.sales_segment_group, form)
            if self.request.matched_route.name == 'sales_segments.copy':
                if len(form.copy_performances.data) == 0:
                    form.copy_performances.errors.append(u'選択してください')
                    return self._render_params(form)

                sales_segment = self.context.sales_segment
                for performance_id in form.copy_performances.data:
                    form.performance_id.data = performance_id
                    id_map = SalesSegment.create_from_template(
                        sales_segment,
                        sales_segment_group_id=sales_segment.sales_segment_group_id,
                        performance_id=performance_id
                    )
                    logger.info('sales_segment copy from:to=%s' % id_map)
                    new_sales_segment = SalesSegment.query.filter_by(id=id_map.get(sales_segment.id)).one()
                    editor.apply_changes(new_sales_segment)

                    if form.copy_products.data:
                        for product in sales_segment.products:
                            Product.create_from_template(
                                template=product,
                                with_product_items=True,
                                performance_id=performance_id,
                                sales_segment=id_map
                            )
            else:
                editor.apply_changes(self.context.sales_segment)
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        return self._render_params(form)


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
            self.context.sales_segment.point_grant_settings.remove(point_grant_setting)
        return_to = self.request.params.get('return_to')
        if return_to is None:
            return_to = self.request.route_path('sales_segments.show', event_id=self.context.event.id, sales_segment_id=self.context.sales_segment.id)
        return HTTPFound(location=return_to)
