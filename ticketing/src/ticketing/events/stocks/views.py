# -*- coding: utf-8 -*-

import logging
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from sqlalchemy.sql import func
from paste.util.multidict import MultiDict

from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Stock, StockAllocation, StockType, Seat, Venue, Performance
from ticketing.events.stocks.forms import StockForms

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap)
class Stocks(BaseView):

    '''
    @view_config(route_name='stocks.allocate_number', request_method='POST', renderer='ticketing:templates/stocks/_form.html')
    def allocate_number(self):
        f = StockForms(self.request.POST)
        for stock_form in f.stock_forms:
            stock_form.form.performance_id.data = f.data.get('performance_id')
            stock_form.form.stock_holder_id.data = f.data.get('stock_holder_id')

        if f.validate():
            for stock_form in f.stock_forms:
                stock = merge_session_with_post(Stock(), stock_form.form.data)
                stock.save()

            self.request.session.flash(u'席数を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'forms':f,
                'allocation_counts':self._get_allocation_count(f.data.get('performance_id')),
            }

    @view_config(route_name='stocks.edit', request_method='GET', renderer='ticketing:templates/stocks/_form.html')
    def edit_get(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        stock_holder_id = int(self.request.matchdict.get('stock_holder_id', 0))

        return {
            'forms':StockForms(performance_id=performance_id, stock_holder_id=stock_holder_id),
            'allocation_counts':self._get_allocation_count(performance_id),
        }

    def _get_allocation_count(self, performance_id):
        allocation_counts = {}
        for sa in StockAllocation.filter_by(performance_id=performance_id).all():
            conditions = {
                'performance_id':performance_id,
                'stock_type_id':sa.stock_type_id,
            }
            sum_quantity = Stock.filter_by(**conditions).with_entities(func.sum(Stock.quantity)).scalar() or 0
            allocation_counts[sa.stock_type_id] = {'total':sa.quantity, 'sum':int(sum_quantity)}

        return allocation_counts
    '''

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
