# -*- coding: utf-8 -*-

from fixture import DataSet
from datetime import datetime

from seed.product import SalesSegmentData
from seed.organization import OrganizationData

class PaymentMethodPluginData(DataSet):
    class RakutenKC:
        name = u'楽天カード決済'
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class RakutenCheckout:
        name = u'楽天安心決済'
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class CvsSEJ:
        name = u'セブンイレブン決済'
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1

class DeliveryMethodPluginData(DataSet):
    class Direct:
        name = u'窓口受取'
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class Send:
        name = u'郵送'
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class CvsSEJ:
        name = u'セブンイレブン受取'
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1

class PaymentMethodData(DataSet):
    class rakuten_kc:
        name        = u'クレジットカード決済'
        fee         = 100
        organization   = OrganizationData.organization_0
        payment_plugin = PaymentMethodPluginData.RakutenKC
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class rakuten_anshin:
        name        = u'楽天あんしん決済'
        fee         = 100
        organization   = OrganizationData.organization_0
        payment_plugin = PaymentMethodPluginData.RakutenCheckout
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class cvs:
        name        = u'セブンイレブン'
        fee         = 100
        organization   = OrganizationData.organization_0
        payment_plugin = PaymentMethodPluginData.CvsSEJ
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1

class DeliveryMethodData(DataSet):
    class send:
        name        = u'郵送'
        fee         = 100
        organization    = OrganizationData.organization_0
        delivery_plugin = DeliveryMethodPluginData.Send
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class window:
        name        = u'窓口受取'
        fee         = 100
        organization    = OrganizationData.organization_0
        delivery_plugin = DeliveryMethodPluginData.Direct
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class cvs:
        name        = u'セブンイレブン'
        fee         = 100
        organization    = OrganizationData.organization_0
        delivery_plugin = DeliveryMethodPluginData.CvsSEJ
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1

class PaymentDeliveryMethodPairData(DataSet):
    class paiment_delivery_method_pair_1:
        transaction_fee = 10
        delivery_fee = 0
        discount    = 0
        discount_unit = 0
        discount_type = 0
        start_at    = None
        end_at      = None
        sales_segment = SalesSegmentData.sales_segment_1
        payment_method = PaymentMethodData.rakuten_kc
        delivery_method = DeliveryMethodData.cvs
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class paiment_delivery_method_pair_2:
        transaction_fee = 20
        delivery_fee = 10
        discount    = 1
        discount_unit = 1
        discount_type = 1
        start_at    = None
        end_at      = None
        sales_segment = SalesSegmentData.sales_segment_1
        payment_method = PaymentMethodData.rakuten_anshin
        delivery_method = DeliveryMethodData.send
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class paiment_delivery_method_pair_3:
        transaction_fee = 20
        delivery_fee = 10
        discount    = 1
        discount_unit = 1
        discount_type = 1
        start_at    = None
        end_at      = None
        sales_segment = SalesSegmentData.sales_segment_2
        payment_method = PaymentMethodData.rakuten_anshin
        delivery_method = DeliveryMethodData.send
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
