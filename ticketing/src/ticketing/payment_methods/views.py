# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.views import BaseView
from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import PaymentMethod
from ticketing.payment_methods.forms import PaymentMethodForm

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class PaymentMethods(BaseView):

    @view_config(route_name='payment_methods.index', renderer='ticketing:templates/payment_methods/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'PaymentMethod.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = PaymentMethod.filter_by(organization_id=self.context.user.organization_id)
        query = query.order_by(sort + ' ' + direction)

        payment_methods = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':PaymentMethodForm(),
            'payment_methods':payment_methods,
        }

    @view_config(route_name='payment_methods.new', request_method='POST', renderer='ticketing:templates/payment_methods/_form.html')
    def new_post(self):
        f = PaymentMethodForm(self.request.POST)
        if f.validate():
            payment_method = merge_session_with_post(PaymentMethod(), f.data)
            payment_method.organization_id = self.context.user.organization_id
            payment_method.save()

            self.request.session.flash(u'決済方法を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='payment_methods.edit', request_method='POST', renderer='ticketing:templates/payment_methods/_form.html')
    def edit_post(self):
        payment_method_id = int(self.request.matchdict.get('payment_method_id', 0))
        payment_method = PaymentMethod.get(payment_method_id)
        if payment_method is None:
            return HTTPNotFound('payment_method id %d is not found' % payment_method_id)

        f = PaymentMethodForm(self.request.POST)
        if f.validate():
            payment_method = merge_session_with_post(payment_method, f.data)
            payment_method.organization_id = self.context.user.organization_id
            payment_method.save()

            self.request.session.flash(u'決済方法を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='payment_methods.delete')
    def delete(self):
        payment_method_id = int(self.request.matchdict.get('payment_method_id', 0))
        payment_method = PaymentMethod.get(payment_method_id)
        if payment_method is None:
            return HTTPNotFound('payment_method id %d is not found' % payment_method_id)

        payment_method.delete()

        self.request.session.flash(u'決済方法を削除しました')
        return HTTPFound(location=route_path('payment_methods.index', self.request))
