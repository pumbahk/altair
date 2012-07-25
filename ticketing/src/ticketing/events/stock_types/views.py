 # -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.core.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Event, StockType
from ticketing.events.stock_types.forms import StockTypeForm

@view_defaults(decorator=with_bootstrap)
class StockTypes(BaseView):

    @view_config(route_name='stock_types.index', renderer='ticketing:templates/stock_types/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        sort = self.request.GET.get('sort', 'StockType.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = StockType.filter(StockType.event_id==event_id)
        query = query.order_by(sort + ' ' + direction)

        stock_types = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':StockTypeForm(event_id=event_id),
            'stock_types':stock_types,
            'event':event,
        }

    @view_config(route_name='stock_types.new', request_method='POST', renderer='ticketing:templates/stock_types/_form.html')
    def new_post(self):
        f = StockTypeForm(self.request.POST)
        if f.validate():
            stock_type = merge_session_with_post(StockType(), f.data)
            stock_type.set_style(f.data)
            stock_type.save()

            self.request.session.flash(u'席種を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='stock_types.edit', request_method='POST', renderer='ticketing:templates/stock_types/_form.html')
    def edit_post(self):
        stock_type_id = int(self.request.matchdict.get('stock_type_id', 0))
        stock_type = StockType.get(stock_type_id)
        if stock_type is None:
            return HTTPNotFound('stock_type id %d is not found' % stock_type_id)

        f = StockTypeForm(self.request.POST)
        if f.validate():
            stock_type = merge_session_with_post(stock_type, f.data)
            stock_type.set_style(f.data)
            stock_type.save()

            self.request.session.flash(u'席種を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='stock_types.delete')
    def delete(self):
        stock_type_id = int(self.request.matchdict.get('stock_type_id', 0))
        stock_type = StockType.get(stock_type_id)
        if stock_type is None:
            return HTTPNotFound('stock_type id %d is not found' % id)

        StockType.delete(stock_type)

        self.request.session.flash(u'席種を削除しました')
        return HTTPFound(location=route_path('events.show', self.request, event_id=stock_type.event_id))
