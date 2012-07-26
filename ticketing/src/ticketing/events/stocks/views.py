# -*- coding: utf-8 -*-

import logging
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from sqlalchemy.sql import func
from paste.util.multidict import MultiDict

from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Stock, StockType, Seat, Venue, Performance

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap)
class Stocks(BaseView):

    @view_config(route_name='stocks.allocate', request_method='POST', renderer='json')
    def allocate(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            logger.error('performance id %d is not found' % performance_id)
            return {
                'result':'error',
                'message':u'不正なデータ',
            }

        post_data = MultiDict(self.request.json_body)
        print post_data
        if not post_data.get('seats') and not post_data.get('stocks') and not post_data.get('stock_types'):
            return {
                'result':'success',
                'message':u'保存対象がありません',
            }

        for post_seat in post_data.get('seats'):
            seat = Seat.filter_by(l0_id=post_seat.get('id'))\
                       .join(Seat.venue)\
                       .filter(Venue.performance_id==performance_id).first()
            seat.stock_id = post_seat.get('stock_id')
            seat.save()

        for post_stock in post_data.get('stocks'):
            stock = Stock.filter_by(id=post_stock.get('id')).first()
            stock.quantity = post_stock.get('quantity')
            stock.save()

        for post_stock_type in post_data.get('stock_types'):
            stock_type = StockType.get(id=post_stock_type.get('id'))
            stock_type.name = post_stock_type.get('name')
            stock_type.style = post_stock_type.get('style')
            stock_type.save()

        return {
            'result':'success',
            'message':u'席種・配券先を保存しました',
        }
