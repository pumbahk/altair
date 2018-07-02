# -*- coding:utf-8 -*-
from datetime import datetime

from altair.app.ticketing.core.models import Host
from altair.sqlahelper import get_db_session

from ..passport.models import PassportUserInfo, PassportUser


def get_passport_product_quantities(products, extra_data):
    # パスポートの商品と、個数のリストを返す
    # 運用で商品のパスポートの表示順と、追加情報のパスポート種類の順番を一緒にしてもらう
    # 種類ごとにパスポートが何件あるか数える
    passport_dict = {}
    for num in range(4):
        index = num + 1
        try:
            if index == 1:
                passport = extra_data['extra'][u"パスポート種類({0}人目)".format(index)]
                birthday = extra_data['extra'][u"生年月日({0}人目)".format(index)]
                sex = extra_data['extra'][u"性別({0}人目)".format(index)]
                if not all([birthday, sex]):
                    # １人目は追加情報に氏名などがない
                    continue
            else:
                passport = extra_data['extra'][u"パスポート種類({0}人目)".format(index)]
                last_name = extra_data['extra'][u"姓({0}人目)".format(index)]
                first_name = extra_data['extra'][u"名({0}人目)".format(index)]
                last_name_kana = extra_data['extra'][u"セイ({0}人目)".format(index)]
                first_name_kana = extra_data['extra'][u"メイ({0}人目)".format(index)]
                birthday = extra_data['extra'][u"生年月日({0}人目)".format(index)]
                sex = extra_data['extra'][u"性別({0}人目)".format(index)]

                if not all([last_name, first_name, last_name_kana, first_name_kana, birthday, sex]):
                    # 正常に一人分の値が入っているかの確認
                    continue

            if passport in passport_dict:
                passport_dict[passport] = passport_dict[passport] + 1
            else:
                passport_dict[passport] = 1
        except KeyError:
            pass

    # 商品の表示順が追加情報のパスポート種類の値と一致しているので商品と件数のペアにする
    product_quantity_pair = []
    for product in products:
        if str(product.display_order) in passport_dict:
            product_quantity_pair.append((product, passport_dict[str(product.display_order)]))
    return product_quantity_pair


def check_order_passport_status(order, passport_user):
    if order.is_canceled():
        return False

    if not passport_user.image_path:
        return False

    if order.payment_status == 'refunding':
        return False

    if order.payment_status == 'refunded':
        return False
    return True


def can_use_passport(request, passport_user):
    now = datetime.now()

    # パスポート設定が使用不可
    if not passport_user.passport.is_valid:
        return False

    # パスポートユーザが使用不可
    if not passport_user.is_valid:
        return False

    # 本人確認用画像が登録されていない
    if not passport_user.image_path:
        return False

    # 平日かどうか
    if passport_user.passport.daily_passport:
        if datetime.now().weekday() in [5, 6]:
            return False

    # パスポートの有効期限切れ確認
    if now > datetime(passport_user.expired_at.year, passport_user.expired_at.month, passport_user.expired_at.day, 23,
                      59):
        return False

    # 入場不可期間
    for term in passport_user.passport.terms:
        if term.start_on <= now <= datetime(term.end_on.year, term.end_on.month, term.end_on.day, 23, 59):
            return False

    # 当日入場済み
    if passport_user.admission_time and passport_user.admission_time.strftime('%Y/%m/%d') == datetime.now().strftime(
            '%Y/%m/%d'):
        return False

    return True


def can_use_passport_order(request, order):
    for user in order.users:
        if not can_use_passport(request, user):
            return False
    return True


def use_passport(passport_user_id):
    passport_user = PassportUser.get(passport_user_id)
    passport_user.admission_time = datetime.now()


def get_passport_user_from_order_id(order_id):
    # データ不整合にならないようマスタから取得
    return PassportUser.query.filter(PassportUser.order_id == order_id).first()


def get_host(request):
    session = get_db_session(request, name="slave")
    host = session.query(Host).filter(Host.organization_id == request.organization.id).first()
    return host


def get_passport_datas(order):
    infos = []
    extra_data = order.attributes
    shipping_address = order.shipping_address
    products_name_dict = get_product_name_dict(order.performance.products)
    passport_user_dict = get_passport_user_dict(order.users)
    for num in range(4):
        index = num + 1
        info = get_passport_data(index, extra_data, shipping_address, products_name_dict, passport_user_dict)
        if info:
            infos.append(info)
    return infos


def get_passport_data(index, extra_data, shipping_address, products_name_dict, passport_user_dict):
    try:
        if index == 1:
            info = PassportUserInfo(
                passport_user_dict[index],
                products_name_dict[extra_data[u"パスポート種類({0}人目)".format(index)]],
                shipping_address.last_name,
                shipping_address.first_name,
                shipping_address.last_name_kana,
                shipping_address.first_name_kana,
                extra_data[u"生年月日({0}人目)".format(index)],
                extra_data[u"性別({0}人目)".format(index)]
            )
        else:
            info = PassportUserInfo(
                passport_user_dict[index],
                products_name_dict[extra_data[u"パスポート種類({0}人目)".format(index)]],
                extra_data[u"姓({0}人目)".format(index)],
                extra_data[u"名({0}人目)".format(index)],
                extra_data[u"セイ({0}人目)".format(index)],
                extra_data[u"メイ({0}人目)".format(index)],
                extra_data[u"生年月日({0}人目)".format(index)],
                extra_data[u"性別({0}人目)".format(index)]
            )
        return info
    except KeyError:
        return None


def get_passport_user_dict(users):
    passport_user_dict = {}
    for user in users:
        passport_user_dict[user.order_attribute_num] = user
    return passport_user_dict


def get_product_name_dict(products):
    products_name_dict = {}
    for product in products:
        if product.display_order in products_name_dict:
            # 商品設計がおかしいがエラーにはしない
            pass
        else:
            products_name_dict[str(product.display_order)] = product.name
    return products_name_dict
