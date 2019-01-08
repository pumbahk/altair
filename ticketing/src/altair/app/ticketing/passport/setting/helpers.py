# encoding: utf-8
from altair.app.ticketing.cart.helpers import japanese_date, error


def get_passport_user_name(shipping_address, order_attributes, order_attribute_num):
    if order_attribute_num == 1:
        name = u"{0} {1}({2} {3})".format(
            shipping_address.last_name,
            shipping_address.first_name,
            shipping_address.last_name_kana,
            shipping_address.first_name_kana,
        )
    else:
        name = u"{0} {1}({2} {3})".format(
            order_attributes[u"姓({0}人目)".format(order_attribute_num)],
            order_attributes[u"名({0}人目)".format(order_attribute_num)],
            order_attributes[u"セイ({0}人目)".format(order_attribute_num)],
            order_attributes[u"メイ({0}人目)".format(order_attribute_num)],
        )
    return name
