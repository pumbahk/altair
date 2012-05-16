 # -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import Event
from ticketing.products.models import StockType, StockTypeEnum
from ticketing.stock_types.forms import StockTypeForm

@view_defaults(decorator=with_bootstrap)
class StockTypes(BaseView):

    @view_config(route_name='stock_types.index', renderer='ticketing:templates/stock_types/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        return {
            'event':event,
        }

    @view_config(route_name='stock_types.new', request_method='POST')
    def new_post(self):
        event_id = int(self.request.matchdict.get('event_id', 0))

        f = StockTypeForm(self.request.POST)
        data = f.data
        stock_type = merge_session_with_post(StockType(), data)
        style = {}
        if stock_type.type == StockTypeEnum.Seat.v:
            style = {
                'stroke' : {
                    'color'     : data.get('stroke_color'),
                    'width'     : data.get('stroke_width'),
                    'pattern'   : data.get('stroke_patten'),
                },
                'fill': {
                    'color'     : data.get('fill_color'),
                    'type'      : data.get('fill_type'),
                    'image'     : data.get('fill_image'),
                },
            }
        stock_type.style = style
        stock_type.event_id = event_id
        stock_type.save()

        self.request.session.flash(u'席種を保存しました')
        return HTTPFound(location=route_path('events.show', self.request, event_id=event_id))

    @view_config(route_name='stock_types.edit', request_method='POST')
    def edit_post(self):
        stock_type_id = int(self.request.matchdict.get('stock_type_id', 0))
        stock_type = StockType.get(stock_type_id)
        if stock_type is None:
            return HTTPNotFound('stock_type id %d is not found' % id)

        f = StockTypeForm(self.request.POST)
        data = f.data
        stock_type.name = data.get('name')
        stock_type.type = data.get('type')
        style = {}
        if stock_type.type == StockTypeEnum.Seat.v:
            style = {
                'stroke' : {
                    'color'     : data.get('stroke_color'),
                    'width'     : data.get('stroke_width'),
                    'pattern'   : data.get('stroke_patten'),
                },
                'fill': {
                    'color'     : data.get('fill_color'),
                    'type'      : data.get('fill_type'),
                    'image'     : data.get('fill_image'),
                },
            }
        stock_type.style = style
        stock_type.save()

        self.request.session.flash(u'席種を保存しました')
        return HTTPFound(location=route_path('events.show', self.request, event_id=stock_type.event_id))

    @view_config(route_name='stock_types.delete')
    def delete(self):
        stock_type_id = int(self.request.matchdict.get('stock_type_id', 0))
        stock_type = StockType.get(stock_type_id)
        if stock_type is None:
            return HTTPNotFound('stock_type id %d is not found' % id)

        StockType.delete(stock_type)

        self.request.session.flash(u'席種を削除しました')
        return HTTPFound(location=route_path('events.show', self.request, event_id=stock_type.event_id))
