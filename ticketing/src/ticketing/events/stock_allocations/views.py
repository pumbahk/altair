 # -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.venues.models import Venue, Seat
from ticketing.events.models import Event, Performance
from ticketing.events.stock_allocations.forms import StockAllocationForm
from ticketing.products.models import StockType, StockTypeEnum, StockAllocation

from sqlalchemy import sql

@view_defaults(decorator=with_bootstrap)
class StockAllocations(BaseView):

    @view_config(route_name='stock_allocations.allocate_number', request_method='POST', renderer='ticketing:templates/stock_allocations/_form.html')
    def allocate_number(self):
        f = StockAllocationForm(self.request.POST)
        if not f.validate():
            return ''

        stock_type = StockType.get(f.data['stock_type_id'])
        if stock_type is None:
            return HTTPNotFound('stock_type id %d is not found' % id)

        stock_allocation = merge_session_with_post(StockAllocation(), f.data)
        stock_allocation.save()

        self.request.session.flash(u'在庫数を保存しました')
        return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)

    @view_config(route_name='stock_allocations.allocate_seat', request_method='POST', renderer='ticketing:templates/stock_allocations/_form.html')
    def allocate_seat(self):
        f = StockAllocationForm(self.request.POST)
        if not f.validate():
            return ''

        stock_type = StockType.get(f.data['stock_type_id'])
        if stock_type is None:
            return HTTPNotFound('stock_type id %d is not found' % id)

        venue = Venue.get(f.data.get('venue_id'))
        if venue is not None:
            Seat.filter(sql.and_(Seat.venue==venue, Seat.l0_id.in_(f.data['seat_l0_id']))).update(synchronize_session=False, values=dict(stock_type_id=stock_type.id))
            f.data.setdefault('performance_id', venue.performance_id)

        stock_allocation = merge_session_with_post(StockAllocation(), f.data)
        stock_allocation.save()

        self.request.session.flash(u'在庫数を保存しました')
        return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
