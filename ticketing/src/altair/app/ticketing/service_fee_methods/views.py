# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from sqlalchemy.sql import func

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import ServiceFeeMethod
from altair.app.ticketing.service_fee_methods.forms import ServiceFeeMethodForm

@view_defaults(decorator=with_bootstrap, permission='master_editor')
class ServiceFeeMethods(BaseView):

    @view_config(route_name='service_fee_methods.index', renderer='altair.app.ticketing:templates/service_fee_methods/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'ServiceFeeMethod.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = ServiceFeeMethod.filter_by(organization_id=self.context.user.organization_id)
        query = query.order_by(sort + ' ' + direction)
        service_fee_methods = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':ServiceFeeMethodForm(),
            'service_fee_methods':service_fee_methods,
        }

    @view_config(route_name='service_fee_methods.new', request_method='GET', renderer='altair.app.ticketing:templates/service_fee_methods/_form.html')
    def new(self):
        return {
            'form': ServiceFeeMethodForm(),
            'action': self.request.route_path('service_fee_methods.new'),
            }

    @view_config(route_name='service_fee_methods.new', request_method='POST', renderer='altair.app.ticketing:templates/service_fee_methods/_form.html')
    def new_post(self):
        f = ServiceFeeMethodForm(self.request.POST)
        if f.validate():
            service_fee_method = merge_session_with_post(ServiceFeeMethod(), f.data)
            service_fee_method.organization_id = self.context.user.organization_id
            service_fee_method.save()

            self.request.session.flash(u'決済方法を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'action': self.request.route_path('service_fee_methods.new'),
            }

    @view_config(route_name='service_fee_methods.edit', request_method='GET', renderer='altair.app.ticketing:templates/service_fee_methods/_form.html')
    def edit(self):
        service_fee_method_id = long(self.request.matchdict.get('service_fee_method_id', 0))
        return {
            'form': ServiceFeeMethodForm(obj=ServiceFeeMethod.query.filter_by(id=service_fee_method_id).one()),
            'action': self.request.route_path('service_fee_methods.edit', service_fee_method_id=service_fee_method_id),
            }

    @view_config(route_name='service_fee_methods.edit', request_method='POST', renderer='altair.app.ticketing:templates/service_fee_methods/_form.html')
    def edit_post(self):
        service_fee_method_id = long(self.request.matchdict.get('service_fee_method_id', 0))
        service_fee_method = ServiceFeeMethod.query.filter_by(id=service_fee_method_id).one()
        if service_fee_method is None:
            return HTTPNotFound('service_fee_method id %d is not found' % service_fee_method_id)

        f = ServiceFeeMethodForm(self.request.POST)
        if f.validate():
            service_fee_method = merge_session_with_post(service_fee_method, f.data)
            service_fee_method.organization_id = self.context.user.organization_id
            service_fee_method.save()

            self.request.session.flash(u'サービス手数料を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'action': self.request.route_path('service_fee_methods.edit', service_fee_method_id=service_fee_method_id),
            }

    @view_config(route_name='service_fee_methods.delete')
    def delete(self):
        service_fee_method_id = int(self.request.matchdict.get('service_fee_method_id', 0))
        service_fee_method = ServiceFeeMethod.get(service_fee_method_id)
        if service_fee_method is None:
            return HTTPNotFound('service_fee_method id %d is not found' % service_fee_method_id)

        location = route_path('service_fee_methods.index', self.request)
        try:
            service_fee_method.delete()
            self.request.session.flash(u'サービス手数料を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)

