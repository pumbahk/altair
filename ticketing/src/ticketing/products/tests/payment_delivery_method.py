# -*- coding: utf-8 -*-

from fixture import DataSet
from datetime import datetime

from ticketing.seed.product import SalesSegmentEvent1Data, SalesSegmentEvent2Data, SalesSegmentEvent3Data
from ticketing.seed.organization import OrganizationData
from ticketing.core.models import FeeTypeEnum

class PaymentMethodPluginData(DataSet):
    class RakutenKC:
        name = u'楽天カード決済'
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class RakutenCheckout:
        name = u'楽天安心決済'
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class CvsSEJ:
        name = u'セブンイレブン決済'
        updated_at  = datetime.now()
        created_at  = datetime.now()

class DeliveryMethodPluginData(DataSet):
    class Direct:
        name = u'窓口受取'
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class Send:
        name = u'郵送'
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class CvsSEJ:
        name = u'セブンイレブン受取'
        updated_at  = datetime.now()
        created_at  = datetime.now()

class PaymentMethodData(DataSet):
    class rakuten_kc:
        name        = u'クレジットカード決済'
        fee         = 100
        fee_type    = FeeTypeEnum.Once.v[0]
        organization   = OrganizationData.organization_0
        payment_plugin = PaymentMethodPluginData.RakutenKC
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class rakuten_anshin:
        name        = u'楽天あんしん決済'
        fee         = 100
        fee_type    = FeeTypeEnum.Once.v[0]
        organization   = OrganizationData.organization_0
        payment_plugin = PaymentMethodPluginData.RakutenCheckout
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class cvs:
        name        = u'セブンイレブン'
        fee         = 100
        fee_type    = FeeTypeEnum.PerUnit.v[0]
        organization   = OrganizationData.organization_0
        payment_plugin = PaymentMethodPluginData.CvsSEJ
        updated_at  = datetime.now()
        created_at  = datetime.now()

class DeliveryMethodData(DataSet):
    class send:
        name        = u'郵送'
        fee         = 100
        fee_type    = FeeTypeEnum.Once.v[0]
        organization    = OrganizationData.organization_0
        delivery_plugin = DeliveryMethodPluginData.Send
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class window:
        name        = u'窓口受取'
        fee         = 100
        fee_type    = FeeTypeEnum.Once.v[0]
        organization    = OrganizationData.organization_0
        delivery_plugin = DeliveryMethodPluginData.Direct
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class cvs:
        name        = u'セブンイレブン'
        fee         = 100
        fee_type    = FeeTypeEnum.PerUnit.v[0]
        organization    = OrganizationData.organization_0
        delivery_plugin = DeliveryMethodPluginData.CvsSEJ
        updated_at  = datetime.now()
        created_at  = datetime.now()

class PaymentDeliveryMethodPairData(DataSet):
    class payment_delivery_method_pair_1:
        system_fee = 10
        transaction_fee = 10
        delivery_fee = 0
        discount    = 0
        discount_unit = 0
        discount_type = 0
        sales_segment = SalesSegmentEvent1Data.sales_segment_1
        payment_method = PaymentMethodData.rakuten_kc
        delivery_method = DeliveryMethodData.cvs
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class payment_delivery_method_pair_2:
        system_fee = 10
        transaction_fee = 20
        delivery_fee = 10
        discount    = 1
        discount_unit = 1
        discount_type = 1
        sales_segment = SalesSegmentEvent1Data.sales_segment_1
        payment_method = PaymentMethodData.rakuten_anshin
        delivery_method = DeliveryMethodData.send
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class payment_delivery_method_pair_3:
        system_fee = 10
        transaction_fee = 20
        delivery_fee = 10
        discount    = 1
        discount_unit = 1
        discount_type = 1
        sales_segment = SalesSegmentEvent1Data.sales_segment_2
        payment_method = PaymentMethodData.rakuten_anshin
        delivery_method = DeliveryMethodData.send
        updated_at  = datetime.now()
        created_at  = datetime.now()
    class payment_delivery_method_pair_4:
        system_fee = 10
        transaction_fee = 300
        delivery_fee = 400
        discount    = 100
        discount_unit = 0
        discount_type = 0
        sales_segment = SalesSegmentEvent3Data.sales_segment_1
        payment_method = PaymentMethodData.rakuten_anshin
        delivery_method = DeliveryMethodData.send
        updated_at  = datetime.now()
        created_at  = datetime.now()
