# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import DeliveryMethod
from altair.app.ticketing.delivery_methods.forms import DeliveryMethodForm

@view_defaults(decorator=with_bootstrap, permission='master_editor')
class DeliveryMethods(BaseView):

    @view_config(route_name='delivery_methods.index', renderer='altair.app.ticketing:templates/delivery_methods/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'DeliveryMethod.display_order')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = DeliveryMethod.filter_by(organization_id=self.context.user.organization_id)
        query = query.order_by('DeliveryMethod.selectable desc') \
                     .order_by(sort + ' ' + direction)

        delivery_methods = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':DeliveryMethodForm(),
            'delivery_methods':delivery_methods,
        }

    @view_config(route_name='delivery_methods.new', request_method='GET', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def new(self):
        return {
            'form': DeliveryMethodForm(),
        }

    @view_config(route_name='delivery_methods.new', request_method='POST', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def new_post(self):
        f = DeliveryMethodForm(self.request.POST)
        if f.validate():
            delivery_method = merge_session_with_post(DeliveryMethod(), f.data)
            delivery_method.organization_id = self.context.user.organization_id
            delivery_method.save()

            self.request.session.flash(u'引取方法を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='delivery_methods.edit', request_method='GET', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def edit(self):
        delivery_method_id = long(self.request.matchdict.get('delivery_method_id', 0))
        return {
            'form': DeliveryMethodForm(obj=DeliveryMethod.query.filter_by(id=delivery_method_id).one()),
        }

    @view_config(route_name='delivery_methods.edit', request_method='POST', renderer='altair.app.ticketing:templates/delivery_methods/_form.html')
    def edit_post(self):
        delivery_method_id = int(self.request.matchdict.get('delivery_method_id', 0))
        delivery_method = DeliveryMethod.get(delivery_method_id)
        if delivery_method is None:
            return HTTPNotFound('delivery_method id %d is not found' % delivery_method_id)

        f = DeliveryMethodForm(self.request.POST)
        if f.validate():
            delivery_method = merge_session_with_post(delivery_method, f.data)
            delivery_method.organization_id = self.context.user.organization_id
            delivery_method.save()

            self.request.session.flash(u'引取方法を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='delivery_methods.delete')
    def delete(self):
        delivery_method_id = int(self.request.matchdict.get('delivery_method_id', 0))
        delivery_method = DeliveryMethod.get(delivery_method_id)
        if delivery_method is None:
            return HTTPNotFound('delivery_method id %d is not found' % delivery_method_id)

        location = route_path('delivery_methods.index', self.request)
        try:
            delivery_method.delete()
            self.request.session.flash(u'引取方法を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)
