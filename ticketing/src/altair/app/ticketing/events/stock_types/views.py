 # -*- coding: utf-8 -*-

import webhelpers.paginate as paginate
from altair.app.ticketing.events.stock_types.api import get_seat_stock_types, get_non_seat_stock_types

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, StockType, StockTypeEnum
from altair.app.ticketing.events.stock_types.forms import StockTypeForm

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class StockTypes(BaseView):

    @view_config(route_name='stock_types.index', renderer='altair.app.ticketing:templates/stock_types/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)
        
        sort = self.request.GET.get('sort', 'StockType.display_order')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        seat_stock_types = paginate.Page(
            StockType.filter_by(event_id=event_id, type=StockTypeEnum.Seat.v).order_by(sort + ' ' + direction),
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        non_seat_stock_types = paginate.Page(
            StockType.filter_by(event_id=event_id, type=StockTypeEnum.Other.v).order_by(sort + ' ' + direction),
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':StockTypeForm(event_id=event_id),
            'seat_stock_types':seat_stock_types,
            'non_seat_stock_types':non_seat_stock_types,
            'event':event,
        }

    @view_config(route_name='stock_types.new', request_method='POST', renderer='altair.app.ticketing:templates/stock_types/_form.html')
    def new_post(self):
        f = StockTypeForm(self.request.POST)
        if f.validate():
            stock_type = merge_session_with_post(StockType(), f.data)
            stock_type.init_display_order(f['event_id'].data)
            stock_type.init_style(f.data)
            stock_type.save()

            self.request.session.flash(u'席種を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='stock_types.edit', request_method='POST', renderer='altair.app.ticketing:templates/stock_types/_form.html')
    def edit_post(self):
        stock_type_id = int(self.request.matchdict.get('stock_type_id', 0))
        stock_type = StockType.get(stock_type_id)
        if stock_type is None:
            return HTTPNotFound('stock_type id %d is not found' % stock_type_id)

        f = StockTypeForm(self.request.POST)
        if f.validate():
            if not 'disp_reports' in self.request.POST:
                f.disp_reports.data = False
            old_display_order = stock_type.display_order
            stock_type = merge_session_with_post(stock_type, f.data)
            stock_type.set_style(f.data)
            stock_type.update_stock_types(old_display_order)

            self.request.session.flash(u'席種を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='stock_types.delete')
    def delete(self):
        stock_type_id = int(self.request.matchdict.get('stock_type_id', 0))
        stock_type = StockType.get(stock_type_id)
        if stock_type is None:
            return HTTPNotFound('stock_type id %d is not found' % stock_type_id)

        location = route_path('events.show', self.request, event_id=stock_type.event_id)
        try:
            stock_type.delete()
            self.request.session.flash(u'席種を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

    @view_config(route_name='stock_types.api.belongs_to_event', request_method="GET", renderer="json")
    def belongs_to_event(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        seat_stock_types = get_seat_stock_types(event_id)
        non_seat_stock_types = get_non_seat_stock_types(event_id)

        html = render_to_response('altair.app.ticketing:templates/stock_types/_list.html',
                                  value={
                                      'event': event,
                                      'seat_stock_types': seat_stock_types,
                                      'non_seat_stock_types': non_seat_stock_types,
                                      'request': self.request,
                                      'mode': 'discount_code'
                                  })

        return {'html': html.body}
