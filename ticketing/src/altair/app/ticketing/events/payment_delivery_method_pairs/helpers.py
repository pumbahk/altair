# -*- coding: utf-8 -*-
import json
from altair.app.ticketing.payments.api import get_payment_delivery_plugin_ids
from altair.app.ticketing.payments.plugins import (
    MULTICHECKOUT_PAYMENT_PLUGIN_ID,
    CHECKOUT_PAYMENT_PLUGIN_ID,
    SEJ_PAYMENT_PLUGIN_ID,
    RESERVE_NUMBER_PAYMENT_PLUGIN_ID,
    FREE_PAYMENT_PLUGIN_ID,
    FAMIPORT_PAYMENT_PLUGIN_ID,
    SHIPPING_DELIVERY_PLUGIN_ID,
    SEJ_DELIVERY_PLUGIN_ID,
    RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
    QR_DELIVERY_PLUGIN_ID,
    ORION_DELIVERY_PLUGIN_ID,
    FAMIPORT_DELIVERY_PLUGIN_ID
)

def default_values_for_pdmp(payment_method_id, delivery_method_id):
    data = get_payment_delivery_plugin_ids(payment_method_id, delivery_method_id)
    pdmp_ids = json.loads(json.dumps(data))
    payment_plugin_id = pdmp_ids['payment_plugin_id']
    delivery_plugin_id = pdmp_ids['delivery_plugin_id']
    if payment_plugin_id == MULTICHECKOUT_PAYMENT_PLUGIN_ID and delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
        data = set_values(
            0,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'true', 'false', 6, 'false', 1,
            'false', 'true', 'false', 3, 'false', 30
        )
    elif payment_plugin_id == CHECKOUT_PAYMENT_PLUGIN_ID and delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
        data = set_values(
            0,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'true', 'false', 6, 'false', 1,
            'false', 'true', 'false', 3, 'false', 30
        )
    elif payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID and delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID:
        data = set_values(
            4,
            'false', 'true', 'false', 1, 'false', 3,
            'false', 'true', 'false', 1, 'false', 0,
            'false', 'true', 'false', 3, 'false', 30
        )
    elif payment_plugin_id == MULTICHECKOUT_PAYMENT_PLUGIN_ID and delivery_plugin_id == SHIPPING_DELIVERY_PLUGIN_ID:
        data = set_values(
            14,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'false', 'true', 1, 'true', 0
        )
    elif payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID and delivery_plugin_id == SHIPPING_DELIVERY_PLUGIN_ID:
        data = set_values(
            17,
            'false', 'true', 'false', 1, 'false', 3,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'false', 'true', 1, 'true', 0
        )
    elif payment_plugin_id == MULTICHECKOUT_PAYMENT_PLUGIN_ID and delivery_plugin_id == QR_DELIVERY_PLUGIN_ID:
        data = set_values(
            0,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'false', 'true', 1, 'true', 0
        )
    elif payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID and delivery_plugin_id == QR_DELIVERY_PLUGIN_ID:
        data = set_values(
            4,
            'false', 'true', 'false', 1, 'false', 3,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'false', 'true', 1, 'true', 0
        )
    elif payment_plugin_id == RESERVE_NUMBER_PAYMENT_PLUGIN_ID and delivery_plugin_id == RESERVE_NUMBER_DELIVERY_PLUGIN_ID:
        data = set_values(
            0,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'false', 'true', 1, 'true', 0,
            'false', 'false', 'true', 1, 'true', 0
        )
    return data

def set_values(*args):
    return {
        # 選択不可期間
        'unavailable_period_days': args[0],
        # 支払期日
        'payment_period_days_one_absolute': args[1],
        'payment_period_days_one_relative': args[2],
        'payment_period_days_two': args[3],
        'payment_period_days_two_selected': args[4],
        'payment_period_days_disabled': args[5],
        'payment_period_days': args[6],
        # コンビニ発券開始日時
        'issuing_interval_days_one_absolute': args[7],
        'issuing_interval_days_one_relative': args[8],
        'issuing_interval_days_two': args[9],
        'issuing_interval_days_two_selected': args[10],
        'issuing_interval_days_disabled': args[11],
        'issuing_interval_days': args[12],
        # コンビニ発券期限日時
        'issuing_end_in_days_one_absolute': args[13],
        'issuing_end_in_days_one_relative': args[14],
        'issuing_end_in_days_two': args[15],
        'issuing_end_in_days_two_selected': args[16],
        'issuing_end_in_days_disabled': args[17],
        'issuing_end_in_days': args[18],
    }
