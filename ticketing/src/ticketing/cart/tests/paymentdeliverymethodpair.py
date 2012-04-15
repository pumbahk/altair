# -*- coding: utf-8 -*-

from fixture import DataSet
from ticketing.products.models import PaymentDeliveryMethodPair
from datetime import datetime
from salessegment import SalesSegmentData
from paymentmethod import PaymentMethodData
from deliverymethod import DeliveryMethodData

class PaymentDeliveryMethodPairData(DataSet):
    class paymentdeliverymethodpair_1:
        sales_segment = SalesSegmentData.salessegment_1
        payment_method = PaymentMethodData.paymentmethod_1
        delivery_method = DeliveryMethodData.deliverymethod_1
        transaction_fee = 5
        delivery_fee = 5
        discount = 0
        discount_unit = 0
        discount_type = 0
        start_at = datetime(2012,7,15,0,0)
        end_at = datetime(2012,7,30,23,59)
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class paymentdeliverymethodpair_2:
        sales_segment = SalesSegmentData.salessegment_1
        payment_method = PaymentMethodData.paymentmethod_2
        delivery_method = DeliveryMethodData.deliverymethod_1
        transaction_fee = 5
        delivery_fee = 5
        discount = 0
        discount_unit = 0
        discount_type = 0
        start_at = datetime(2012,7,15,0,0)
        end_at = datetime(2012,7,30,23,59)
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class paymentdeliverymethodpair_3:
        sales_segment = SalesSegmentData.salessegment_1
        payment_method = PaymentMethodData.paymentmethod_3
        delivery_method = DeliveryMethodData.deliverymethod_1
        transaction_fee = 5
        delivery_fee = 5
        discount = 0
        discount_unit = 0
        discount_type = 0
        start_at = datetime(2012,7,15,0,0)
        end_at = datetime(2012,7,30,23,59)
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
