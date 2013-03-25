# -*- coding: utf-8 -*-

import json
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Event, Performance, SalesSegment, SalesSegmentGroup, Product, PaymentDeliveryMethodPair
from ticketing.events.payment_delivery_method_pairs.forms import PaymentDeliveryMethodPairForm
from ticketing.events.sales_segments.forms import SalesSegmentForm
from ticketing.memberships.forms import MemberGroupForm
from ticketing.users.models import MemberGroup, Membership
from webob.multidict import MultiDict

from datetime import datetime

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class SalesSegments(BaseView):
    def _form(self, formdata=None):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment_group_id = int(self.request.params.get('sales_segment_group_id') or 0)
        performance_id = int(self.request.params.get('performance_id') or 0)

        if sales_segment_id:
            _formdata = formdata
            sales_segment = SalesSegment.get(sales_segment_id)
            if sales_segment is None:
                return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)
            kwargs = dict(
                obj=sales_segment,
                sales_segment_groups=[sales_segment.sales_segment_group],
                performances=sales_segment.sales_segment_group.event.performances,
                new_form=False
            )
        else:
            _formdata = MultiDict() if formdata is None else formdata.copy()
            sales_segment_groups = None
            if performance_id:
                _formdata['performance_id'] = performance_id
                sales_segment_groups = Performance.get(performance_id).event.sales_segment_groups
            if sales_segment_group_id:
                sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id)
                _formdata['sales_segment_group_id'] = sales_segment_group_id
                kwargs = dict(
                    performances=sales_segment_group.event.performances,
                    sales_segment_groups=sales_segment_groups,
                    new_form=True
                    )
            else:
                kwargs = dict(
                    new_form=True,
                    sales_segment_groups=sales_segment_groups
                    )

        return SalesSegmentForm(formdata=_formdata, **kwargs)

    @property
    def performance(self):
        if 'performance_id' not in self.request.params:
            return None

        performance_id = self.request.params['performance_id']
        return Performance.query.filter(Performance.id==performance_id).first()

    @property
    def sales_segment_group(self):
        if 'sales_segment_group_id' not in self.request.params:
            return None

        performance_id = self.request.params['sales_segment_group_id']
        return Performance.query.filter(Performance.id==performance_id).first()

    def _pdmp_map(self, sales_segment_groups):
        """ 販売区分グループごとのPDMP json
        """

        mapped = {}
        for ssg in sales_segment_groups:
            mapped[str(ssg.id)] = [(pdmp.id, pdmp.payment_method.name + " - " + pdmp.delivery_method.name) 
                              for pdmp in ssg.payment_delivery_method_pairs]

        return json.dumps(mapped)

    @property
    def sales_segment_groups(self):
        performance = self.performance
        if performance is None:
            return []

        return performance.event.sales_segment_groups

    @view_config(route_name='sales_segments.new', request_method='GET', renderer='ticketing:templates/sales_segments/_form.html', xhr=True)
    def new_xhr(self):
        return {
            'form': self._form(),
            'action': self.request.path,
            'pdmp_map': self._pdmp_map(self.sales_segment_groups)
            }

    @view_config(route_name='sales_segments.new', request_method='POST', renderer='ticketing:templates/sales_segments/_form.html', xhr=True)
    def new_post(self):
        f = self._form(self.request.POST)

        if f.validate():
            if f.start_at.data is None:
                f.start_at.data = datetime.now()
            if f.end_at.data is None:
                f.end_at.data = datetime.now()
            sales_segment = merge_session_with_post(SalesSegment(), f.data)
            pdmps = PaymentDeliveryMethodPair.query.filter(PaymentDeliveryMethodPair.id.in_(f.payment_delivery_method_pairs.data)).filter(PaymentDeliveryMethodPair.sales_segment_group_id==sales_segment.sales_segment_group_id).all()
            sales_segment.payment_delivery_method_pairs = pdmps
            sales_segment.save()

            self.request.session.flash(u'販売区分を作成しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'action': self.request.path_url,
                'pdmp_map': self._pdmp_map(self.sales_segment_groups)
                }

    @view_config(route_name='sales_segments.edit', request_method='GET', renderer='ticketing:templates/sales_segments/_form.html', xhr=True)
    def edit_xhr(self):
        return {
            'form': self._form(),
            'action': self.request.path,
            'pdmp_map': self._pdmp_map(self.sales_segment_groups)
            }

    def _edit_post(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            raise HTTPBadRequest(body=json.dumps({
                'message':u'販売区分が存在しません',
            }))

        f = SalesSegmentForm(self.request.POST, performances=sales_segment.sales_segment_group.event.performances)
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

    @view_config(route_name='sales_segments.edit', request_method='POST', renderer='ticketing:templates/sales_segments/_form.html', xhr=True)
    def edit_post_xhr(self):
        f = self._edit_post()
        if f is None:
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'action': self.request.path_url,
                'pdmp_map': self._pdmp_map(self.sales_segment_groups)
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
