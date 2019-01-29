# -*- coding: utf-8 -*-

"""
クーポン・割引コード機能に関するメソッドで汎用的に使えるものをまとめてあります
"""

import math
from datetime import datetime
from itertools import groupby

from altair.app.ticketing.cart.exceptions import NotAllowedBenefitUnitError, DiscountCodeInternalError, \
    OwnDiscountCodeDuplicateError
from altair.app.ticketing.core.models import Event, Performance, StockType
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from .models import (
    DiscountCodeTargetStockType,
    DiscountCodeSetting,
    UsedDiscountCodeCart,
    UsedDiscountCodeOrder,
    DiscountCodeCode,
    DiscountCodeTarget)
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.utils import rand_string
from altair.sqlahelper import get_db_session
from altair.viewhelpers import DateTimeHelper, create_date_time_formatter
from pyramid.httpexceptions import HTTPFound
from pyramid.threadlocal import get_current_request
from sqlalchemy import func, and_, or_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from webhelpers import paginate as paginate


def save_target_stock_type_data(stock_type_id_list, setting_id, event_id, performance_id):
    """
    適用席種を登録する
    :param list stock_type_id_list:
    :param int setting_id:
    :param int event_id:
    :param int performance_id:
    :return: void
    """
    for st_id in stock_type_id_list:
        data = DiscountCodeTargetStockType()
        data.discount_code_setting_id = setting_id
        data.event_id = event_id
        data.performance_id = performance_id
        data.stock_type_id = st_id
        data.save()


def get_performances_of_dc_setting(session, setting_id):
    """
    クーポン・割引コード設定IDに紐付いている公演を取得するクエリ
    :param SessionMaker session: スレーブセッション
    :param int setting_id: クーポン・割引コード設定ID
    :return LogicalDeletableQuery: クエリオブジェクト
    """
    return session.query(
        Performance
    ).join(
        DiscountCodeTargetStockType, DiscountCodeTargetStockType.performance_id == Performance.id
    ).join(
        Event, DiscountCodeTargetStockType.event_id == Event.id
    ).filter(
        DiscountCodeTargetStockType.discount_code_setting_id == setting_id
    ).group_by(
        Performance.id
    ).order_by(
        Event.id.desc(),
        Performance.start_on.asc()
    )


def get_dc_target_stock_type_of_performances(session, p_ids, setting_id):
    """
    公演とクーポン・割引コード設定に紐づく登録済適用席種情報の取得するクエリ
    :param SessionMaker session: スレーブセッション
    :param list p_ids: ページネーションで表示される公演のIDリスト
    :param int setting_id: クーポン・割引コード設定ID
    :return LogicalDeletableQuery: クエリオブジェクト
    """
    return session.query(
        DiscountCodeTargetStockType.id,
        Event.id.label('event_id'),
        Event.title.label('event_title'),
        Performance.id.label('performance_id'),
        Performance.name.label('performance_name'),
        Performance.start_on.label('performance_start_on'),
        StockType.id.label('stock_type_id'),
        StockType.name.label('stock_type_name')
    ).join(
        Performance, DiscountCodeTargetStockType.performance_id == Performance.id
    ).join(
        Event, DiscountCodeTargetStockType.event_id == Event.id
    ).join(
        StockType, DiscountCodeTargetStockType.stock_type_id == StockType.id
    ).filter(
        DiscountCodeTargetStockType.performance_id.in_(p_ids),
        DiscountCodeTargetStockType.discount_code_setting_id == setting_id
    ).group_by(
        DiscountCodeTargetStockType.id
    ).order_by(
        Event.id.desc(),
        Performance.start_on.asc(),
        StockType.id.asc()
    )


def get_stock_type_id_list_by_discount_code_setting_id(setting_id):
    """
    クーポン・割引コード設定IDに紐づく適用席種IDをリスト形式で取得
    :param setting_id:
    :return:
    """
    ids = get_db_session(get_current_request(), 'slave').query(
        DiscountCodeTargetStockType.id
    ).filter_by(discount_code_setting_id=setting_id).order_by(
        DiscountCodeTargetStockType.id
    ).all()

    result = [r for r in ids]
    return result


def get_choices_of_search_events(organization_id):
    """
    ORGに紐づくイベント情報をSelectFieldのchoicesで扱える形式にして取得
    :param long organization_id: ORG ID
    :return list: イベントIDとタイトルのタプルによるリスト
    """

    events = get_db_session(get_current_request(), 'slave').query(
        Event.id,
        Event.title
    ).filter(
        Event.organization_id == organization_id
    ).order_by(
        Event.created_at.desc()
    )

    return [('', u'(イベントを選んでください。)')] + [(e.id, e.title) for e in events]


def get_choices_of_search_performances(performance_id):
    """
    公演情報をSelectFieldのchoicesで扱える形式にして取得
    :param unicode performance_id: 公演ID
    :return:
    """
    pfm = get_db_session(get_current_request(), 'slave').query(
        Performance.id,
        Performance.name,
        Performance.start_on
    ).filter_by(id=performance_id).first()

    dthelper = DateTimeHelper(create_date_time_formatter(None))
    return [(pfm.id, u'{name} ({start_on})'.format(
        name=pfm.name,
        start_on=dthelper.datetime(pfm.start_on, with_weekday=True)
    ))]


def check_discount_code_functions_available(context, request):
    """
    管理画面のクーポン・割引コード関連機能が使用できる状態か判定
    :param DiscountCodeCodesResource or PerformanceAdminResource context: Resourceオブジェクト
    :param Request request: requestは使用できていないが、使用場所がcustom_predicatesのために必要。
    :return: Boolean
    """
    # ログアウト状態
    if not context.user:
        return False

    # 組織設定でクーポン・割引コード設定がOFF
    if not context.user.organization.setting.enable_discount_code:
        return False

    # クーポン・割引コード設定のIDがGETで渡されている場合
    if 'setting_id' in request.matchdict:
        setting_id = request.matchdict['setting_id']
        try:
            # 成功時はcontextに設定情報を渡しておく
            context.setting = context.session.query(DiscountCodeSetting).filter_by(
                organization_id=context.user.organization_id,
                id=setting_id
            ).one()
        except NoResultFound:
            return False
        except MultipleResultsFound:
            request.session.flash(u'登録データに不整合が発生しています。開発部に調査を依頼してください。')
            raise HTTPFound(location=request.route_path('discount_code.settings_index'))

    return True


def is_exist_duplicate_codes(code, code_str_list):
    """
    入力されたコードの中で重複があればTrueを返す
    :param unicode code: クーポン・割引コード文字列
    :param list code_str_list: 入力された全クーポン・割引コード文字列のリスト
    :return:
    """
    n = sum(code == x for x in code_str_list)
    return n > 1


def get_discount_price_from_carted_product(request, cp):
    """
    カートに入った商品ごとの割引総額を取得
    :param Request request: リクエストオブジェクト
    :param cp: CartedProductオブジェクト
    :return: discount_price: 商品ごとの割引金額。
    """
    from altair.app.ticketing.cart.models import CartedProductItem
    result = get_db_session(request, 'slave').query(
        func.sum(UsedDiscountCodeCart.applied_amount).label('discount_price')
    ).join(
        CartedProductItem
    ).filter(
        CartedProductItem.carted_product_id == cp.id
    ).one()

    return result.discount_price if result.discount_price else 0


def get_discount_price_from_ordered_product(op):
    """
    予約の商品ごとの割引総額を取得
    :param op: OrderedProductオブジェクト
    :return: discount_price: 商品ごとの割引金額。
    """
    from altair.app.ticketing.orders.models import OrderedProductItem
    result = get_db_session(get_current_request(), 'slave').query(
        func.sum(UsedDiscountCodeOrder.applied_amount).label('discount_price')
    ).join(
        OrderedProductItem
    ).filter(
        OrderedProductItem.ordered_product_id == op.id
    ).one()

    return result.discount_price if result.discount_price else 0


def calc_applied_amount(setting, item):
    """
    クーポン・割引コードによる適用金額（値引き額）を計算する。
    :param DiscountCodeSetting setting: クーポン・割引コード設定
    :param CartedProductItem item: カートに入った商品明細
    :return int amount: 計算された金額
    """
    if setting.benefit_unit == u'%':
        # 小数点以下は切り捨て
        amount = math.floor(float(item.price) * (setting.benefit_amount / 100.00))
    elif setting.benefit_unit == u'y':
        # 商品明細価格よりクーポン・割引コードの設定金額が大きい場合は、商品明細価格が割引の上限
        amount = min([setting.benefit_amount, item.price])
    else:
        raise NotAllowedBenefitUnitError()

    return int(amount)


def save_discount_code(carted_product_item, ordered_product_item):
    """
    対象のCartedProductItemにクーポン・割引コードが使用されていたら、UsedDiscountCodeOrderにデータを記録する
    :param CartedProductItem carted_product_item: カートに入った商品明細
    :param OrderedProductItem ordered_product_item: オーダーとして登録する作成途中の商品明細データ
    :return bool:
    """
    used_discount_code_carts = carted_product_item.used_discount_codes
    now = datetime.now()

    for index, used_discount_code_cart in enumerate(used_discount_code_carts):
        use_discount_code_order = UsedDiscountCodeOrder()
        use_discount_code_order.code = used_discount_code_cart.code
        use_discount_code_order.ordered_product_item = ordered_product_item
        use_discount_code_order.ordered_product_item_token = ordered_product_item.tokens[index]
        use_discount_code_order.discount_code_setting_id = used_discount_code_cart.discount_code_setting_id
        use_discount_code_order.applied_amount = used_discount_code_cart.applied_amount
        use_discount_code_order.benefit_amount = used_discount_code_cart.benefit_amount
        use_discount_code_order.benefit_unit = used_discount_code_cart.benefit_unit

        # クーポン・割引コードテーブルに使用日時を記載
        if used_discount_code_cart.discount_code_id:
            use_discount_code_order.discount_code_id = used_discount_code_cart.discount_code_id
            available_code = DiscountCodeCode.query.filter_by(id=used_discount_code_cart.discount_code_id).first()
            available_code.used_at = now
            available_code.save()
        use_discount_code_order.add()

        # UsedDiscountCodeCartテーブルにカート処理日時を記載
        used_discount_code_cart.finished_at = now
    return True


def get_discount_code_settings(codes):
    """
    使用されたクーポン・割引コード文字列からクーポン・割引コード設定を取得する
    使用後のコード設定を取得することが目的なので、有効フラグや有効期間などは無視する。
    :param list codes: UsedDiscountCodeCartのリスト
    :return list setting_list: DiscountCodeSettingのリスト
    """
    setting_list = []
    code_set = set(code.code[:4] for code in codes)

    for code in code_set:
        first_digit = code[:1]
        following_2to4_digits = code[1:4]
        setting = DiscountCodeSetting \
            .filter(DiscountCodeSetting.first_digit == first_digit) \
            .filter(DiscountCodeSetting.following_2to4_digits == following_2to4_digits) \
            .one()
        setting_list.append(setting)

    return setting_list


def used_discount_code_groups(cart_or_order):
    """
    使用されたクーポン・割引コード情報をグループ化し、その合計金額や設定内容をまとめている
    :param cart_or_order: OrderやCartオブジェクト
    :return list res: クーポン・割引コード設定IDでグループ化されたdict
        例):
            groups = {5L: {
                        'explanation': u'<p><strong>イーグルスダミークーポン 23%OFF</strong></p>',
                        'detail': [{
                            'item_name': u'テスト席種2の商品',
                            'applied_amount': 230L,
                            'code': u'EEQT00000002',
                            'item_price': 1000}
                        ]}
                    },
                    ...
                    ...
    """

    # ソート後、必要な情報のみリストにまとめる
    codes = get_used_discount_codes(cart_or_order)
    sorted_codes = sorted(codes, key=lambda x: (x.discount_code_setting_id, x.id))
    tmp = []
    for sc in sorted_codes:
        if hasattr(sc, 'carted_product_item'):
            item_name = sc.carted_product_item.product_item.name
            item_price = int(sc.carted_product_item.price)
        elif hasattr(sc, 'ordered_product_item'):
            item_name = sc.ordered_product_item.product_item.name
            item_price = int(sc.ordered_product_item.price)
        else:
            raise KeyError('lacked with necessary product_item information.')

        tmp.append({
            'setting_id': sc.discount_code_setting_id,
            'explanation': sc.discount_code_setting.explanation,
            'detail': {
                'code': sc.code,
                'item_name': item_name,
                'item_price': item_price,
                'applied_amount': sc.applied_amount
            }
        })

    # クーポン・割引コード設定IDをキーにグループ化
    groups = {}
    for (k, g) in groupby(tmp, key=lambda x: (x['setting_id'], x['explanation'])):
        setting_id = k[0]
        explanation = k[1]
        groups[setting_id] = {
            'explanation': explanation,
            'detail': []
        }
        for itm in g:
            groups[setting_id]['detail'].append(itm['detail'])

    return groups


def validate_to_delete_all_codes(setting, session):
    """
    全コードを削除する前のバリデーション
    :param DiscountCodeSetting setting: クーポン・割引コード設定
    :param SessionMaker session: スレーブセッション
    :return:
    """
    err = []
    try:
        if DiscountCodeSetting.is_valid_checked(setting.id, session):
            err.append(u'設定の有効フラグにチェックが入っている')
    except NoResultFound:
        err.append(u'削除対象の割引設定（ID: {} {}）が存在しません。'.format(setting.id, setting.name))
    except MultipleResultsFound:
        err.append(u'複数の割引設定（ID: {} {}）が検出されました。開発部に調査を依頼してください。'.format(setting.id, setting.name))

    valid_order_cnt = UsedDiscountCodeOrder.count_exists_valid_order(setting.first_4_digits, session)
    if valid_order_cnt:
        err.append(u'コードが使用された有効な予約が{}件ある'.format(valid_order_cnt))

    return err


def paginate_setting_list(query, request):
    """
    クーポン・割引コード設定の一覧画面におけるページネーション
    デフォルトのソートは「有効期間（終了日時）の降順 > クーポン・割引コードIDの降順」
    :param LogicalDeletableQuery query: クエリオブジェクト
    :param Request request: リクエストオブジェクト
    :return webhelpers.paginate.Page : クーポン・割引コード設定のページネーション
    """
    sort = request.GET.get('sort', 'DiscountCodeSetting.end_at')
    direction = request.GET.get('direction', 'desc')
    query = query.order_by(
        '{0} {1}'.format(sort, direction),
        'DiscountCodeSetting.id desc'
    )

    return paginate.Page(
        query,
        page=int(request.params.get('page', 0)),
        items_per_page=20,
        url=PageURL_WebOb_Ex(request)
    )


def insert_specific_number_code(num, first_4_digits, data):
    """
    ユニークなコードを生成し、既存のレコードと重複がないことを確かめてインサート
    :param int num: コード生成数
    :param unicode first_4_digits: コードの頭4桁
    :param dict data: 発行されたコードのレコードへの付加情報
    :return bool:
    """
    for _ in range(num):
        code = DiscountCodeCode()
        code.discount_code_setting_id = data['discount_code_setting_id']
        code.organization_id = data['organization_id']
        code.operator_id = data['operator_id']
        code.code = make_code_str(first_4_digits, data)
        code.add()


def make_code_str(first_4_digits, data):
    """
    コードの生成を行う, 既存コードと重複あれば生成をループ
    :param unicode first_4_digits: コードの頭4桁
    :param dict data: 発行されたコードのレコードへの付加情報
    :return unicode code_str: ORG単位でユニークなコード文字列
    """
    code_str = first_4_digits + rand_string(DiscountCodeCode.AVAILABLE_LETTERS, 8)
    if _if_generating_code_exists(code_str, data['organization_id']):
        return code_str
    else:
        make_code_str(first_4_digits, data)


def _if_generating_code_exists(code, organization_id):
    """
    すでに作成済のコードではないか確認する
    :param str code: ランダムに生成されたコード文字列
    :param int organization_id:
    :return: boolean Trueなら未作成のコード、Falseなら作成済み
    """
    try:
        DiscountCodeCode.query.filter(
            DiscountCodeCode.organization_id == organization_id,
            DiscountCodeCode.code == code,
        ).one()
        return False
    except NoResultFound:
        return True


def delete_all_discount_code(setting_id):
    """
    既存のコードを全削除する
    :param setting_id: クーポン・割引コード設定ID
    :return: 削除したコードの総数
    """
    query = DiscountCodeCode.query.filter_by(discount_code_setting_id=setting_id)
    count = query.count()
    if count > 0:
        codes = query.all()
        for code in codes:
            code.delete()

    return count


def find_available_target_settings_query(performance_id, stock_type_ids, issued_by=None, first_4_digits=None,
                                         max_price=None, session=None, refer_all=False, now=None):
    """
    指定された条件で利用可能なクーポン・割引コード設定を抽出するクエリを作成
    :param int performance_id: 公演ID
    :param set stock_type_ids: 席種IDのセット型
    :param issued_by: コード管理元
    :param first_4_digits: クーポン・割引コードの頭4文字
    :param Decimal max_price: 最も高い席の価格（例：大人席・子供席なら大人席の値段）
    :param SessionMaker session: スレーブセッション
    :param bool refer_all: Trueなら「有効・無効フラグ」や「有効期間」を無視して抽出する。
    :param datetime now: 現在時刻。「時間指定してカート購入」を利用している場合はそちらの時刻が使用される。
    :return LogicalDeletableQuery q: クエリオブジェクト
    """

    q = session.query(DiscountCodeSetting) if session else DBSession.query(DiscountCodeSetting)
    q = q.outerjoin(
        DiscountCodeTarget,
        DiscountCodeTargetStockType
    ).group_by(
        DiscountCodeSetting.id
    )

    if max_price:
        q = q.filter(
            or_(
                and_(
                    DiscountCodeTarget.performance_id == performance_id,
                    DiscountCodeSetting.condition_price_amount >= max_price
                ),
                and_(
                    DiscountCodeTargetStockType.stock_type_id.in_(stock_type_ids),
                    DiscountCodeTargetStockType.performance_id == performance_id
                )
            ))
    else:
        q = q.filter(
            or_(
                DiscountCodeTarget.performance_id == performance_id,
                and_(
                    DiscountCodeTargetStockType.stock_type_id.in_(stock_type_ids),
                    DiscountCodeTargetStockType.performance_id == performance_id
                )
            ))

    if not refer_all:
        if now is None:
            now = datetime.now()

        q = q.filter(
            DiscountCodeSetting.is_valid == 1,
            or_(DiscountCodeSetting.start_at.is_(None), DiscountCodeSetting.start_at <= now),
            or_(DiscountCodeSetting.end_at.is_(None), DiscountCodeSetting.end_at >= now)
        )

    if issued_by is not None:
        q = q.filter(DiscountCodeSetting.issued_by == issued_by)

    if first_4_digits is not None:
        q = q.filter(
            DiscountCodeSetting.first_digit == first_4_digits[:1],
            DiscountCodeSetting.following_2to4_digits == first_4_digits[1:4]
        )

    return q


def find_available_target_settings(performance_id, stock_type_ids, issued_by=None, first_4_digits=None,
                                   max_price=None, session=None, refer_all=False, now=None):
    """
    引数で指定された条件で利用可能な状態の割引設定を抽出。
    :param int performance_id: 公演ID
    :param set stock_type_ids: 席種IDのセット型
    :param SessionMaker session: スレーブセッション
    :param issued_by: コードの発行元
    :param first_4_digits: クーポン・割引コードの頭4文字
    :param Decimal max_price: 最も高い席の価格（例：大人席・子供席なら大人席の値段）
    :param bool refer_all: Trueなら「有効・無効フラグ」や「有効期間」を無視して抽出する。
    :param datetime now: 現在時刻。「時間指定してカート購入」を利用している場合はそちらの時刻が使用される。
    :return: クーポン・割引コード設定のリスト（ただしfirst_4_digitsがある場合、返り値は1つであるべきなので、.one()で返す）
    """

    q = find_available_target_settings_query(performance_id, stock_type_ids, session=session, issued_by=issued_by,
                                             first_4_digits=first_4_digits,
                                             max_price=max_price, refer_all=refer_all,
                                             now=now)

    if first_4_digits is not None:
        try:
            return q.one()
        except NoResultFound:
            return []
        except MultipleResultsFound as e:
            raise DiscountCodeInternalError('duplicated settings found: {}'.format(e.message))

    return q.all()


def get_used_discount_codes(order_like):
    """
    order_likeには、cartと、_DummyCart、Orderが入る想定
    :param order_like: Cart、Order、_DummyCartなど処理によって異なるオブジェクト。データの構造が同じ。
    :return list codes_list: UsedDiscountCodeCartのリスト
    """
    codes_list = list()
    for item in order_like.items:
        for element in item.elements:
            codes_list.extend(element.used_discount_codes)
    return codes_list


def is_already_used_code(code, organization_id, session):
    """
    すでに使用済みのコードではないかチェック
    :param unicode code: 入力されたコード文字列
    :param long organization_id: ORG ID
    :param SessionMaker session: スレーブセッション
    :return bool: True 使われている / False 未使用
    """
    used_code = session.query(
        UsedDiscountCodeOrder
    ).filter(
        UsedDiscountCodeOrder.code == code,
        UsedDiscountCodeOrder.canceled_at.is_(None),
        UsedDiscountCodeOrder.refunded_at.is_(None)
    ).order_by(
        UsedDiscountCodeOrder.created_at.desc()
    ).first()

    if used_code:
        return True

    # 管理画面で「使用済みにする」ボタンが押されていた場合を考慮
    try:
        session.query(
            DiscountCodeCode
        ).filter(
            DiscountCodeCode.code == code,
            DiscountCodeCode.used_at.is_(None),
            DiscountCodeCode.organization_id == organization_id
        ).one()
    except MultipleResultsFound as e:
        # 複数見つかった場合は生成されている自社コードにデータ不整合が起こっている
        raise OwnDiscountCodeDuplicateError(
            'multiple own issued codes found. check DiscountCode table!: {}'.format(e.message)
        )
    except NoResultFound:
        return False


def release_cart(cart):
    """
    UsedDiscountCodeCartのリリース。
    TODO: 使用箇所が一つしかないのでメソッド化する必要がないと思う
    :param Cart cart: カートオブジェクト
    :return:
    """
    codes = get_used_discount_codes(cart)
    for code in codes:
        code.finished_at = datetime.now()
    return True


def get_used_discount_quantity(order_like):
    """
    クーポン・割引コードの使用された数
    :param order_like: Cart、Order、_DummyCartなど処理によって異なるオブジェクト。データの構造が同じ。
    :return:
    """
    quantity = 0
    for item in order_like.items:
        for element in item.elements:
            used_codes = element.used_discount_codes
            if used_codes:
                quantity = quantity + len(used_codes)
    return quantity


def get_discount_amount(order_like):
    """
    1予約あたりの合計割引金額
    :param order_like: Cart、Order、_DummyCartなど処理によって異なるオブジェクト。データの構造が同じ。
    :return:
    """
    discount_amount = 0
    for item in order_like.items:
        for element in item.elements:
            used_codes = element.used_discount_codes
            if used_codes:
                for used in used_codes:
                    discount_amount = discount_amount + used.applied_amount
    return discount_amount


def get_discount_price(ordered_product_item_token):
    """
    商品明細単位あたりのクーポン・割引コードによる割引額を合算している
    :param ordered_product_item_token: 商品明細
    :return: 割引額
    """
    price = 0
    used_codes = ordered_product_item_token.used_discount_codes
    if used_codes:
        for used in used_codes:
            price = price + used.applied_amount
    return price
