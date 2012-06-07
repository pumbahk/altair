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
from ticketing.events.stocks.forms import StockForms
from ticketing.products.models import StockType, StockTypeEnum, Stock, StockHolder

@view_defaults(decorator=with_bootstrap)
class Stocks(BaseView):

    @view_config(route_name='stocks.allocate_number', request_method='POST', renderer='ticketing:templates/stocks/_form.html')
    def allocate_number(self):
        f = StockForms(self.request.POST)
        if f.validate():
            for stock_form in f.stock_forms:
                stock = merge_session_with_post(Stock(), stock_form.form.data)
                stock.stock_holder_id = f.data.get('stock_holder_id')
                stock.save()

            self.request.session.flash(u'席数を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'forms':f,
            }

    @view_config(route_name='stocks.edit', request_method='GET', renderer='ticketing:templates/stocks/_form.html')
    def edit_get(self):
        stock_holder_id = int(self.request.matchdict.get('stock_holder_id', 0))
        return {
            'forms':StockForms(stock_holder_id=stock_holder_id),
        }
