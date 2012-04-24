# -*- coding: utf-8 -*-

from fixture import DataSet
from datetime import datetime

from seed.client import ClientData

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
        client      = ClientData.client_0
        payment_plugin = PaymentMethodPluginData.RakutenKC
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class rakuten_anshin:
        name        = u'楽天あんしん決済'
        fee         = 100
        client      = ClientData.client_0
        payment_plugin = PaymentMethodPluginData.RakutenCheckout
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class cvs:
        name        = u'セブンイレブン'
        fee         = 100
        client      = ClientData.client_0
        payment_plugin = PaymentMethodPluginData.CvsSEJ
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1

class DeliveryMethodData(DataSet):
    class send:
        name        = u'郵送'
        fee         = 100
        client      = ClientData.client_0
        delivery_plugin = DeliveryMethodPluginData.Send
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class window:
        name        = u'窓口受取'
        fee         = 100
        client      = ClientData.client_0
        delivery_plugin = DeliveryMethodPluginData.Direct
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1
    class cvs:
        name        = u'セブンイレブン'
        fee         = 100
        client      = ClientData.client_0
        delivery_plugin = DeliveryMethodPluginData.CvsSEJ
        updated_at  = datetime.now()
        created_at  = datetime.now()
        status      = 1