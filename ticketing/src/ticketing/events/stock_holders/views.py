# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import Event, Performance, Account, SalesSegment
from ticketing.events.performances.forms import PerformanceForm
from ticketing.events.stock_holders.forms import StockHolderForm
from ticketing.events.sales_segments.forms import SalesSegmentForm
from ticketing.events.stock_types.forms import StockTypeForm, StockAllocationForm
from ticketing.products.models import Product, StockHolder
from ticketing.products.forms import ProductForm, ProductItemForm

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class StockHolders(BaseView):

    @view_config(route_name='stock_holders.new', request_method='POST', renderer='ticketing:templates/stock_holders/_form.html')
    def new_post(self):
        performance_id = int(self.request.POST.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = StockHolderForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            stock_holder = merge_session_with_post(StockHolder(), f.data)
            style = {
                'text':f.data.get('text'),
                'text_color':f.data.get('text_color'),
            }
            stock_holder.style = style
            stock_holder.save()

            self.request.session.flash(u'枠を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='stock_holders.edit', request_method='POST', renderer='ticketing:templates/stock_holders/_form.html')
    def edit_post(self):
        stock_holder_id = int(self.request.matchdict.get('stock_holder_id', 0))
        stock_holder = StockHolder.get(stock_holder_id)
        if stock_holder is None:
            return HTTPNotFound('stock_holder id %d is not found' % stock_holder_id)

        f = StockHolderForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            stock_holder = merge_session_with_post(stock_holder, f.data)
            style = {
                'text':f.data.get('text'),
                'text_color':f.data.get('text_color'),
            }
            stock_holder.style = style
            stock_holder.save()

            self.request.session.flash(u'枠を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='stock_holders.delete')
    def delete(self):
        stock_holder_id = int(self.request.matchdict.get('stock_holder_id', 0))
        stock_holder = StockHolder.get(stock_holder_id)
        if stock_holder is None:
            return HTTPNotFound('stock_holder id %d is not found' % stock_holder_id)

        stock_holder.delete()

        self.request.session.flash(u'枠を削除しました')
        return HTTPFound(location=route_path('performances.show', self.request, performance_id=stock_holder.performance.id, _anchor='seat-allocation'))
