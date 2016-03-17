# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import SalesSegmentGroup, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod
from altair.app.ticketing.events.payment_delivery_method_pairs.forms import PaymentDeliveryMethodPairForm
from altair.app.ticketing.service_fee_methods.api import get_system_fee_default, SystemFeeDefaultDoesNotExist, SystemFeeDefaultDuplicated
from . import helpers as h

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class PaymentDeliveryMethodPairs(BaseView):
    @view_config(route_name='payment_delivery_method_pairs.new', request_method='GET', renderer='altair.app.ticketing:templates/payment_delivery_method_pairs/edit.html')
    def new_get(self):
        sales_segment_group_id = int(self.request.matchdict.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id)

        f = PaymentDeliveryMethodPairForm(organization_id=self.context.user.organization_id)
        f.sales_segment_group_id.data = sales_segment_group_id

        try:
            system_fee, system_fee_type = get_system_fee_default(organization_id=self.context.user.organization_id)
        except SystemFeeDefaultDoesNotExist:
            system_fee = f.system_fee.default
            system_fee_type = f.system_fee_type.default
        except SystemFeeDefaultDuplicated:
            system_fee = f.system_fee.default
            system_fee_type = f.system_fee_type.default

        return {
            'form':f,
            'sales_segment_group':sales_segment_group,
            'payment_methods':PaymentMethod.filter_by(organization_id=self.context.user.organization_id).all(),
            'delivery_methods':DeliveryMethod.filter_by(organization_id=self.context.user.organization_id).all(),
            'system_fee': system_fee,
            'system_fee_type': system_fee_type,
        }

    @view_config(route_name='payment_delivery_method_pairs.default_values_for_pdmp', renderer='json')
    def get_payment_delivery_plugin(self):
        return h.default_values_for_pdmp(
            self.request.GET.get('payment_plugin_id'),
            self.request.GET.get('delivery_plugin_id')
        )

    @view_config(route_name='payment_delivery_method_pairs.new', request_method='POST', renderer='altair.app.ticketing:templates/payment_delivery_method_pairs/edit.html')
    def new_post(self):
        sales_segment_group_id = int(self.request.POST.get('sales_segment_group_id', 0))
        sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id)
        if sales_segment_group is None:
            raise HTTPNotFound('sales_segment_group_id %d is not found' % sales_segment_group_id)

        f = PaymentDeliveryMethodPairForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            payment_delivery_method_pair = merge_session_with_post(PaymentDeliveryMethodPair(), f.data)
            payment_delivery_method_pair.payment_method_id = f.data['payment_method_id']
            payment_delivery_method_pair.delivery_method_id = f.data['delivery_method_id']
            payment_delivery_method_pair.save()

            # Add new payment_delivery_method_pair to each sales_segment in sales_segment_group
            for sales_segment in sales_segment_group.sales_segments:
                sales_segment.payment_delivery_method_pairs.append(payment_delivery_method_pair)
                sales_segment.save()

            self.request.session.flash(u'決済・引取方法を登録しました')
            return HTTPFound(location=route_path('sales_segment_groups.show', self.request, sales_segment_group_id=f.sales_segment_group_id.data))
        else:
            try:
                system_fee, system_fee_type = get_system_fee_default(organization_id=self.context.user.organization_id)
            except SystemFeeDefaultDoesNotExist:
                system_fee = f.system_fee.default
                system_fee_type = f.system_fee_type.default
            except SystemFeeDefaultDuplicated:
                system_fee = f.system_fee.default
                system_fee_type = f.system_fee_type.default
                
            return {
                'form':f,
                'sales_segment_group':sales_segment_group,
                'payment_methods':PaymentMethod.filter_by(organization_id=self.context.user.organization_id).all(),
                'delivery_methods':DeliveryMethod.filter_by(organization_id=self.context.user.organization_id).all(),
                'system_fee': system_fee,
                'system_fee_type': system_fee_type,                
            }

    @view_config(route_name='payment_delivery_method_pairs.edit', request_method='GET', renderer='altair.app.ticketing:templates/payment_delivery_method_pairs/edit.html')
    def edit_get(self):
        id = int(self.request.matchdict.get('payment_delivery_method_pair_id', 0))
        pdmp = PaymentDeliveryMethodPair.get(id)
        if pdmp is None:
            return HTTPNotFound('payment_delivery_method_pair id %d is not found' % id)

        f = PaymentDeliveryMethodPairForm(organization_id=self.context.user.organization_id, obj=pdmp)
        return {
            'form':f,
            'sales_segment_group':pdmp.sales_segment_group,
            'payment_methods':[pdmp.payment_method],
            'delivery_methods':[pdmp.delivery_method],
        }

    @view_config(route_name='payment_delivery_method_pairs.edit', request_method='POST', renderer='altair.app.ticketing:templates/payment_delivery_method_pairs/edit.html')
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

            self.request.session.flash(u'決済・引取方法を登録しました')
            return HTTPFound(location=route_path('sales_segment_groups.show', self.request, sales_segment_group_id=pdmp.sales_segment_group_id))
        else:
            self.request.session.flash(u'決済・引取方法の登録に失敗しました')
            return {
                'form':f,
                'sales_segment_group':pdmp.sales_segment_group,
                'payment_methods':[pdmp.payment_method],
                'delivery_methods':[pdmp.delivery_method],
            }

    @view_config(route_name='payment_delivery_method_pairs.delete')
    def delete(self):
        id = int(self.request.matchdict.get('payment_delivery_method_pair_id', 0))
        pdmp = PaymentDeliveryMethodPair.get(id)
        if pdmp is None:
            return HTTPNotFound('payment_delivery_method_pair id %d is not found' % id)

        # Delete entries from association table for this pdmp
        for sales_segment in pdmp.sales_segment_group.sales_segments:
            if pdmp in sales_segment.payment_delivery_method_pairs:
                sales_segment.payment_delivery_method_pairs.remove(pdmp)
                sales_segment.save()

        location = route_path('sales_segment_groups.show', self.request, sales_segment_group_id=pdmp.sales_segment_group_id)
        try:
            pdmp.delete()
            self.request.session.flash(u'決済・引取方法を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)
