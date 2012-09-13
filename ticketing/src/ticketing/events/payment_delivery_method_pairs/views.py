# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.core.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import SalesSegment, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod
from ticketing.events.payment_delivery_method_pairs.forms import PaymentDeliveryMethodPairForm

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class PaymentDeliveryMethodPairs(BaseView):

    @view_config(route_name='payment_delivery_method_pairs.new', request_method='GET', renderer='ticketing:templates/payment_delivery_method_pairs/edit.html')
    def new_get(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)

        f = PaymentDeliveryMethodPairForm(organization_id=self.context.user.organization_id)
        f.sales_segment_id.data = sales_segment_id
        return {
            'form':f,
            'sales_segment':sales_segment,
            'payment_methods':PaymentMethod.filter_by(organization_id=self.context.user.organization_id).all(),
            'delivery_methods':DeliveryMethod.filter_by(organization_id=self.context.user.organization_id).all(),
        }

    @view_config(route_name='payment_delivery_method_pairs.new', request_method='POST', renderer='ticketing:templates/payment_delivery_method_pairs/edit.html')
    def new_post(self):
        sales_segment_id = int(self.request.matchdict.get('sales_segment_id', 0))
        sales_segment = SalesSegment.get(sales_segment_id)
        if sales_segment is None:
            return HTTPNotFound('sales_segment id %d is not found' % sales_segment_id)

        f = PaymentDeliveryMethodPairForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            payment_delivery_method_pair = merge_session_with_post(PaymentDeliveryMethodPair(), f.data)
            payment_delivery_method_pair.sales_segment_id = sales_segment_id
            payment_delivery_method_pair.payment_method_id = f.data['payment_method_id']
            payment_delivery_method_pair.delivery_method_id = f.data['delivery_method_id']
            payment_delivery_method_pair.save()

            self.request.session.flash(u'販売区分を登録しました')
            return HTTPFound(location=route_path('sales_segments.show', self.request, sales_segment_id=sales_segment.id))
        else:
            return {
                'form':f,
                'sales_segment':sales_segment,
                'payment_methods':PaymentMethod.filter_by(organization_id=self.context.user.organization_id).all(),
                'delivery_methods':DeliveryMethod.filter_by(organization_id=self.context.user.organization_id).all(),
            }

    @view_config(route_name='payment_delivery_method_pairs.edit', request_method='GET', renderer='ticketing:templates/payment_delivery_method_pairs/edit.html')
    def edit_get(self):
        id = int(self.request.matchdict.get('payment_delivery_method_pair_id', 0))
        pdmp = PaymentDeliveryMethodPair.get(id)
        if pdmp is None:
            return HTTPNotFound('payment_delivery_method_pair id %d is not found' % id)

        f = PaymentDeliveryMethodPairForm(organization_id=self.context.user.organization_id)
        f.process(record_to_multidict(pdmp))
        f.payment_method_id.data = pdmp.payment_method_id
        f.delivery_method_id.data = pdmp.delivery_method_id
        return {
            'form':f,
            'sales_segment':pdmp.sales_segment,
        }

    @view_config(route_name='payment_delivery_method_pairs.edit', request_method='POST', renderer='ticketing:templates/payment_delivery_method_pairs/edit.html')
    def edit_post(self):
        id = int(self.request.matchdict.get('payment_delivery_method_pair_id', 0))
        pdmp = PaymentDeliveryMethodPair.get(id)
        if pdmp is None:
            return HTTPNotFound('payment_delivery_method_pair id %d is not found' % id)

        f = PaymentDeliveryMethodPairForm(self.request.POST, organization_id=self.context.user.organization_id)
        f.id.data = id
        f.payment_method_id.data = pdmp.payment_method_id
        f.delivery_method_id.data = pdmp.delivery_method_id
        if f.validate():
            payment_delivery_method_pair = merge_session_with_post(PaymentDeliveryMethodPair(), f.data)
            payment_delivery_method_pair.save()

            self.request.session.flash(u'販売区分を登録しました')
            return HTTPFound(location=route_path('sales_segments.show', self.request, sales_segment_id=pdmp.sales_segment_id))
        else:
            return {
                'form':f,
                'sales_segment':pdmp.sales_segment
            }

    @view_config(route_name='payment_delivery_method_pairs.delete')
    def delete(self):
        id = int(self.request.matchdict.get('payment_delivery_method_pair_id', 0))
        pdmp = PaymentDeliveryMethodPair.get(id)
        if pdmp is None:
            return HTTPNotFound('payment_delivery_method_pair id %d is not found' % id)

        pdmp.delete()

        self.request.session.flash(u'販売区分を削除しました')
        return HTTPFound(location=route_path('sales_segments.show', self.request, sales_segment_id=pdmp.sales_segment_id))
