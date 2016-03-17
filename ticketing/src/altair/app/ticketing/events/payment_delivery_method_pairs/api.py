#-*- coding: utf-8 -*-
from altair.app.ticketing.core.models import PaymentMethod, DeliveryMethod

def get_payment_delivery_plugin_ids(payment_method_id, delivery_method_id):
    payment_plugin_id = PaymentMethod.filter_by(id=payment_method_id).one().payment_plugin_id
    delivery_plugin_id = DeliveryMethod.filter_by(id=delivery_method_id).one().delivery_plugin_id

    return {
        'payment_plugin_id': payment_plugin_id,
        'delivery_plugin_id': delivery_plugin_id
    }
