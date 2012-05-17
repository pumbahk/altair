# encoding: utf-8

from ticketing.seed import DataSet
from ticketing.orders.models import Order, OrderedProduct, OrderedProductItem
from .product import *
from .venue import *
from .user import *

class ShippingAddressData(DataSet):
    class shipping_address_1:
        user = UserData.user_1
        first_name = u'小泉'
        last_name = u'森太郎'
        first_name_kana = u'コイズミ'
        last_name_kana = u'モリタロウ'
        zip = u'141-0022'
        prefecture = u'東京都'
        city = u'品川区'
        address_1 = u'東五反田5-21-15'
        address_2 = u'メタリオンOSビル 7F'
        country = u'日本国'
        tel_1 = u'03-0000-0000'
        tel_2 = u'090-0000-0000'
        fax = u'03-0000-0000'
        status = 0

    class shipping_address_2:
        user = UserData.user_1
        first_name = u'松居'
        last_name = u'健太郎'
        first_name_kana = u'マツイ'
        last_name_kana = u'ケンタロウ'
        zip = u'141-0022'
        prefecture = u'東京都'
        city = u'品川区'
        address_1 = u'東五反田5-21-15'
        address_2 = u'メタリオンOSビル 7F'
        country = u'日本国'
        tel_1 = u'03-0000-0000'
        tel_2 = u'090-0000-0000'
        fax = u'03-0000-0000'
        status = 0

class OrderData(DataSet):
    class order_1:
        user = UserData.user_1
        shipping_address = ShippingAddressData.shipping_address_1
        total_amount = 12000
        status = 0

    class order_2:
        user = UserData.user_2
        shipping_address = ShippingAddressData.shipping_address_2
        total_amount = 7000
        status = 0

class OrderedProductOrder1Data(DataSet):
    class ordered_product_1:
        order = OrderData.order_1
        product = ProductEvent1Data.product_1
        price = 8000
        status = 0

    class ordered_product_2:
        order = OrderData.order_1
        product = ProductEvent1Data.product_2
        price = 4000
        status = 0

class OrderedProductOrder2Data(DataSet):
    class ordered_product_1:
        order = OrderData.order_2
        product = ProductEvent1Data.product_3
        price = 7000
        status = 0

class OrderedProductItemOrder1Data(DataSet):
    class ordered_product_item_1:
        ordered_product = OrderedProductOrder1Data.ordered_product_1
        product_item = ProductItemEvent1Performance1Data.productitem_1
        price = 8000
        status = 0

    class ordered_product_item_2:
        ordered_product = OrderedProductOrder1Data.ordered_product_2
        product_item = ProductItemEvent1Performance1Data.productitem_2
        price = 4000
        status = 0

class OrderedProductItemOrder2Data(DataSet):
    class ordered_product_item_1:
        ordered_product = OrderedProductOrder2Data.ordered_product_1
        product_item = ProductItemEvent1Performance1Data.productitem_3
        price = 7000
        status = 0
