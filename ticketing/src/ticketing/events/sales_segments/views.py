# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import Event, SalesSegment
from ticketing.events.payment_delivery_method_pair.forms import PaymentDeliveryMethodPairForm
from ticketing.events.sales_segments.forms import SalesSegmentForm

@view_defaults(decorator=with_bootstrap)
class SalesSegments(BaseView):

    @view_config(route_name='sales_segments.index', renderer='ticketing:templates/sales_segments/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        conditions = {
            'event_id':event.id
        }
        sales_segments = SalesSegment.find_by(**conditions)

        return {
            'form_sales_segment':SalesSegmentForm(event_id=event_id),
            'sales_segments':sales_segments,
            'event':event,
        }

    @view_config(route_name='sales_segments.show', renderer='ticketing:templates/sales_segments/show.html')
    def show(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        form_ss = SalesSegmentForm()
        form_ss.process(record_to_multidict(sales_segment))

        return {
            'form_ss':form_ss,
            'form_pdmp':PaymentDeliveryMethodPairForm(),
            'sales_segment':sales_segment,
        }

    @view_config(route_name='sales_segments.new', request_method='POST', renderer='ticketing:templates/sales_segments/_form.html')
    def new_post(self):
        event_id = int(self.request.POST.get('event_id', 0))
        if not event_id:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = SalesSegmentForm(self.request.POST)
        if f.validate():
            sales_segment = merge_session_with_post(SalesSegment(), f.data)
            sales_segment.event_id = event_id
            sales_segment.save()

            self.request.session.flash(u'販売区分を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='sales_segments.edit', request_method='POST', renderer='ticketing:templates/sales_segments/_form.html')
    def edit_post(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        f = SalesSegmentForm(self.request.POST)
        if f.validate():
            sales_segment = merge_session_with_post(sales_segment, f.data)
            sales_segment.save()

            self.request.session.flash(u'販売区分を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='sales_segments.delete')
    def delete(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        event_id = sales_segment.event_id
        sales_segment.delete()

        self.request.session.flash(u'販売区分を削除しました')
        return HTTPFound(location=route_path('sales_segments.index', self.request, event_id=event_id))
