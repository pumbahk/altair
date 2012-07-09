# -*- coding:utf-8 -*-

import sys
import sqlahelper
from pyramid.paster import bootstrap

import ticketing.core.models as c_model


def main():
    session = sqlahelper.get_session()

    ini_file = sys.argv[1]
    env = bootstrap(ini_file)

    org = c_model.Organization(
        id = 10,
        name = u'BJ89ers',
        code = u'B8',
        client_type = c_model.OrganizationTypeEnum.Standard.v,
        city = u'',
        street = u'',
        address = u'',
        other_address = u'',
        tel_1 = u'',
        tel_2 = u'',
        fax = u'',
        prefecture = u'',
        status = 1
    )
    session.add(org)

    payment_method1 = c_model.PaymentMethod(
        name = 'コンビニ支払い',
        fee = 0,
        fee_type = c_model.FeeTypeEnum.Once.v,
        organization = org,
        payment_plugin_id = 1
    )
    payment_method2 = c_model.PaymentMethod(
        name = 'クレジットカード払い',
        fee = 0,
        fee_type = c_model.FeeTypeEnum.Once.v,
        organization = org,
        payment_plugin_id = 3
    )
    delivery_method = c_model.DeliveryMethod(
        name = u'なし',
        fee = 0,
        fee_type = c_model.FeeTypeEnum.Once.v,
        organization = org,
        delivery_plugin_id = 1
    )
    session.add(payment_method1)
    session.add(payment_method2)
    session.add(delivery_method)

    account = c_model.Account(
        account_type = c_model.AccountTypeEnum.Promoter.v,
        name = u'89ers'
    )
    session.add(account)

    event = c_model.Event(
        account = account,
        code = 'BJ890',
        title = u'FC会員登録 89ers',
        abbreviated_title = 'bj89ers'
    )
    session.add(event)

    stock_type_1 = c_model.StockType(
        name = u'会員権',
        type = c_model.StockTypeEnum.Other.v,
        quantity_only = True
    )
    stock_type_2 = c_model.StockType(
        name = u'Tシャツ',
        type = c_model.StockTypeEnum.Other.v,
        quantity_only = True
    )
    session.add(stock_type_1)
    session.add(stock_type_2)

    from datetime import datetime
    sales_segment = c_model.SalesSegment(
        name = u'',
        kind = c_model.SalesSegmentKindEnum.other.v,
        start_at = datetime(2012,07,01,00,00),
        end_at = datetime(2012,8,31,00,00),
        upper_limit = 10000,
        seat_choice = False,
        event = event,
    )
    session.add(sales_segment)

    product1 = c_model.Product(
        name = u'法人会員',
        price = 100000,
        sales_segment = sales_segment,
        event = event
    )
    product2 = c_model.Product(
        name = u'プレミアム会員',
        price = 30000,
        sales_segment = sales_segment,
        event = event
    )
    product3 = c_model.Product(
        name = u'レギュラー会員',
        price = 30000,
        sales_segment = sales_segment,
        event = event
    )
    session.add(product1)
    session.add(product2)
    session.add(product3)

    session.flush()

    performance = c_model.Performance(
        name = u'FC会員登録２０１２',
        code = 'B8REG2012000',
        open_on = None,
        start_on = None,
        end_on =  None,
        event_id = event.id,
        venue = None,
    )
    session.add(performance)
    session.flush()

main()

