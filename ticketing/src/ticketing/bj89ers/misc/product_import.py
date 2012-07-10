# -*- coding:utf-8 -*-

import sys
import sqlahelper
from pyramid.paster import bootstrap
import sqlalchemy
from sqlalchemy import engine_from_config

import ticketing.core.models as c_model
import ticketing.operators.models as o_model
import hashlib

import transaction
def main():
    if len(sys.argv) < 2:
        print "python product_import.py development.ini"
        sys.exit()
    ini_file = sys.argv[1]
    env = bootstrap(ini_file)

    session = sqlahelper.get_session()
    t = transaction.begin()

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

    role = session.query(o_model.OperatorRole).filter_by(name='administrator').one()

    auth = o_model.OperatorAuth(
        login_id= u'dev+bj01@ticketstar.jp',
        password=hashlib.md5('admin').hexdigest(),
        auth_code=u'auth_code',
        access_token=u'access_token',
        secret_key=u'secret_key'
    )
    session.add(auth)

    operator = o_model.Operator(
        name = 'bj89ers',
        email = 'dev+bj01@ticketstar.jp',
        roles=[role],
        expire_at=None,
        status=1,
        organization=org,
        auth=auth
    )
    session.add(operator)

    payment_method1 = c_model.PaymentMethod(
        name = 'コンビニ支払い',
        fee = 0,
        fee_type = c_model.FeeTypeEnum.Once.v[0],
        organization = org,
        payment_plugin = c_model.PaymentMethodPlugin.get(1)
    )
    payment_method2 = c_model.PaymentMethod(
        name = 'クレジットカード払い',
        fee = 0,
        fee_type = c_model.FeeTypeEnum.Once.v[0],
        organization = org,
        payment_plugin = c_model.PaymentMethodPlugin.get(3)
    )
    delivery_method = c_model.DeliveryMethod(
        name = u'なし',
        fee = 0,
        fee_type = c_model.FeeTypeEnum.Once.v[0],
        organization = org,
        delivery_plugin = c_model.DeliveryMethodPlugin.get(1)
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
        organization = org,
        account = account,
        code = 'BJ890',
        title = u'仙台89ers FC会員登録',
        abbreviated_title = 'bj89ers'
    )
    session.add(event)
    performance = c_model.Performance(
        name = u'FC会員登録２０１２',
        code = 'B8REG2012000',
        open_on = None,
        start_on = None,
        end_on =  None,
        venue = None,
    )
    session.add(performance)
    event.performances.append(performance)

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
        name = u'会員登録',
        kind = c_model.SalesSegmentKindEnum.other.v,
        start_at = datetime(2012,07,01,00,00),
        end_at = datetime(2012,8,31,00,00),
        upper_limit = 10000,
        seat_choice = False,
        event = event,
    )
    session.add(sales_segment)

    pdmp1 = c_model.PaymentDeliveryMethodPair(
        system_fee = 0,
        transaction_fee = 0,
        delivery_fee = 0,
        discount = 0,
        discount_unit = 0,
        payment_period_days = 3,
        issuing_interval_days = 1,
        issuing_start_at = None,
        issuing_end_at = None,
        sales_segment = sales_segment,
        payment_method = payment_method1,
        delivery_method = delivery_method
    )
    pdmp2 = c_model.PaymentDeliveryMethodPair(
        system_fee = 0,
        transaction_fee = 0,
        delivery_fee = 0,
        discount = 0,
        discount_unit = 0,
        payment_period_days = 3,
        issuing_interval_days = 1,
        issuing_start_at = None,
        issuing_end_at = None,
        sales_segment = sales_segment,
        payment_method = payment_method2,
        delivery_method = delivery_method
    )
    session.add(pdmp1)
    session.add(pdmp2)

    stock_holder = c_model.StockHolder(
        name = u'test',
        event_id = event.id,
        account_id = account.id,
        style = None
    )

    stock_status_1 = c_model.StockStatus(
        quantity = 100
    )
    session.add(stock_status_1)
    stock_1 = c_model.Stock(
        quantity = 1000,
        performance_id = performance.id,
        stock_holder_id = stock_holder.id,
        stock_type_id = stock_type_1.id,
        stock_status = stock_status_1
    )
    session.add(stock_1)

    stock_status_2 = c_model.StockStatus(
        quantity = 100,
    )
    session.add(stock_status_2)
    stock_2 = c_model.Stock(
        quantity = 1000,
        performance_id = performance.id,
        stock_holder_id = stock_holder.id,
        stock_type_id = stock_type_1.id,
        stock_status = stock_status_2
    )
    session.add(stock_2)


    product1 = c_model.Product(
        name = u'法人会員',
        price = 100500,
        sales_segment = sales_segment,
        event = event
    )
    session.add(product1)

    product_item1_1 = c_model.ProductItem(
        item_type = '',
        price = 100500,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_1,
        quantity = 50
    )
    session.add(product_item1_1)
    product_item1_2 = c_model.ProductItem(
        item_type = '',
        price = 0,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_2,
        quantity = 50
    )
    session.add(product_item1_2)

    product2 = c_model.Product(
        name = u'プラチナ会員',
        price = 30000,
        sales_segment = sales_segment,
        event = event
    )
    session.add(product2)

    product_item2_1 = c_model.ProductItem(
        item_type = '',
        price = 30000,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_1,
        quantity = 50
    )
    session.add(product_item2_1)
    product_item2_2 = c_model.ProductItem(
        item_type = '',
        price = 0,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_2,
        quantity = 50
    )
    session.add(product_item2_2)

    product3 = c_model.Product(
        name = u'ゴールド会員',
        price = 10000,
        sales_segment = sales_segment,
        event = event
    )
    session.add(product3)

    product_item3_1 = c_model.ProductItem(
        item_type = '',
        price = 10000,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_1,
        quantity = 50
    )
    session.add(product_item3_1)
    product_item3_2 = c_model.ProductItem(
        item_type = '',
        price = 0,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_2,
        quantity = 50
    )
    session.add(product_item3_2)

    product4 = c_model.Product(
        name = u'レギュラー会員',
        price = 3000,
        sales_segment = sales_segment,
        event = event
    )
    session.add(product4)

    product_item4_1 = c_model.ProductItem(
        item_type = '',
        price = 3000,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_1,
        quantity = 50
    )
    session.add(product_item4_1)

    product5 = c_model.Product(
        name = u'ライト会員',
        price = 1000,
        sales_segment = sales_segment,
        event = event
    )
    session.add(product5)

    product_item5_1 = c_model.ProductItem(
        item_type = '',
        price = 1000,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_1,
        quantity = 50
    )
    session.add(product_item5_1)

    product5 = c_model.Product(
        name = u'ジュニア会員',
        price = 1000,
        sales_segment = sales_segment,
        event = event
    )
    session.add(product5)

    product_item5_1 = c_model.ProductItem(
        item_type = '',
        price = 1000,
        product_id =product1.id,
        performance_id = performance.id,
        stock = stock_1,
        quantity = 50
    )
    session.add(product_item5_1)

    session.flush()


    t.commit()

main()

