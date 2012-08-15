# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.stock_holders.forms import StockHolderForm
from ticketing.core.models import Event, StockHolder

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class StockHolders(BaseView):

    @view_config(route_name='stock_holders.index', renderer='ticketing:templates/stock_holders/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)

        sort = self.request.GET.get('sort', 'StockHolder.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        conditions = {
            'event_id':event.id
        }
        query = StockHolder.filter_by(**conditions)
        query = query.order_by(sort + ' ' + direction)

        stock_holders = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=2,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form_stock_holder':StockHolderForm(organization_id=self.context.user.organization_id, event_id=event_id),
            'stock_holders':stock_holders,
            'event':event,
        }

    @view_config(route_name='stock_holders.new', request_method='POST', renderer='ticketing:templates/stock_holders/_form.html')
    def new_post(self):
        event_id = int(self.request.POST.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

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
        return HTTPFound(location=route_path('events.show', self.request, event_id=stock_holder.event.id))
