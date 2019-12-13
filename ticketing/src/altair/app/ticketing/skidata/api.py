# -*- coding: utf-8 -*-
import logging
from datetime import datetime, date

from altair.app.ticketing.skidata.exceptions import SkidataSendWhitelistError
from altair.app.ticketing.skidata.models import SkidataBarcode, SkidataPropertyEntry, SkidataPropertyTypeEnum
from altair.app.ticketing.orders.models import OrderedProductItemToken
from altair.skidata.api import make_whitelist
from altair.skidata.exceptions import SkidataWebServiceError
from altair.skidata.interfaces import ISkidataSession
from altair.skidata.models import TSAction, TSOption, HSHErrorType, HSHErrorNumber, WhitelistRecord

logger = logging.getLogger(__name__)


def create_new_barcode(order_no):
    """
    指定した予約番号を元に、SkidataBarcodeデータを新規に生成する。
    :param order_no: 予約番号
    """
    opi_tokens = OrderedProductItemToken.find_all_by_order_no(order_no)
    for token in opi_tokens:
        SkidataBarcode.insert_new_barcode(token.id)


def send_whitelist_if_necessary(request, order_no, fail_silently=False):
    """
    Skidata連携ONの公演の予約が支払済みで公演が今日、そしてSkidataBarcodeが未連携の場合はSkidataへWhitelistを送信する
    :param request: リクエスト
    :param order_no: 予約番号
    :param fail_silently: エラーの場合にExceptionをraiseしないかどうか
    """
    whitelist = []
    barcode_list = []
    for barcode in SkidataBarcode.find_all_by_order_no(order_no):
        token = barcode.ordered_product_item_token
        ordered_product_item = token.item
        ordered_product = ordered_product_item.ordered_product
        order = ordered_product.order

        product_item = ordered_product_item.product_item
        performance = product_item.performance
        if not (order.paid_at is not None and performance.start_on.date() == date.today()
                and performance.event.organization.setting.enable_skidata
                and performance.event.setting.enable_skidata
                and barcode.sent_at is None and barcode.canceled_at is None):
            continue
        # 支払済で公演の開演日が今日、公演のORGとイベント設定がSkidata連携ON、
        # そして SkidataBarcode の sent_at と canceled_at が無い場合は
        # Skidataへwhitelistを送信するのでWhitelistRecordを作成する
        # Whitelistのexpireは公演の開演年の12月31日 23:59:59
        expire = datetime(year=performance.start_on.year, month=12, day=31, hour=23, minute=59, second=59)
        whitelist.append(
            make_whitelist(action=TSAction.INSERT, qr_code=barcode.data,
                           ts_option=create_ts_option_from_token(token), expire=expire)
        )
        barcode_list.append(barcode)

    skidata_session = request.registry.queryUtility(ISkidataSession)
    if whitelist and skidata_session is not None:
        send_whitelist_to_skidata(skidata_session, whitelist, barcode_list, fail_silently)


def update_barcode_to_refresh_order(order_no, existing_barcode_list):
    """
    予約更新に伴うSkidataBarcode更新を実施する。
    指定した予約番号と、更新前のSkidataBarcodeのリストを元に予約更新によるSkidataBarcode.ordered_product_item_tokenの更新や、
    バーコードの追加・削除などを実施する。
    :param order_no: 予約番号
    :param existing_barcode_list: 更新前の予約に紐づく既存のSkidataBarcodeリスト
    """
    barcode_and_token_to_update = list()  # 既存のSkidataBarcodeにひもづくOrderedProductItemTokenを更新するためのリスト
    barcode_list_to_cancel = list()  # 予約更新で削除されたSkidataBarcodeを削除するためのリスト
    tokens_to_add_barcode = list()  # 予約更新で追加されたOrderedProductItemTokenにSkidataBarcodeを追加するためのリスト

    new_opi_tokens = OrderedProductItemToken.find_all_by_order_no(order_no)
    for existing_barcode in existing_barcode_list:
        existing_token = existing_barcode.ordered_product_item_token
        equivalent_token = find_equivalent_token_from_list(existing_token, new_opi_tokens)
        if equivalent_token:
            barcode_and_token_to_update.append((existing_barcode, equivalent_token))
        else:
            barcode_list_to_cancel.append(existing_barcode)

    tokens_to_update_barcode = [token for _, token in barcode_and_token_to_update]
    for new_token in new_opi_tokens:
        if new_token not in tokens_to_update_barcode:  # 更新リストにない場合は、追加とみなす(商品明細追加や商品個数追加など)
            tokens_to_add_barcode.append(new_token)

    for barcode, token in barcode_and_token_to_update:  # SkidataBarcodeのordered_product_item_tokenの置き換え
        SkidataBarcode.update_token(barcode.id, token.id)
    for barcode in barcode_list_to_cancel:  # 予約更新後に存在しないバーコードをキャンセル
        SkidataBarcode.cancel(barcode.id)
    for token in tokens_to_add_barcode:  # 予約更新後に追加されたOrderedProductItemTokenにバーコードを付与
        SkidataBarcode.insert_new_barcode(token.id)


def find_equivalent_token_from_list(target_token, token_list):
    """
    リストから予約更新前後で等価となるOrderedProductItemTokenを取得する
    :param target_token: 対象のOrderedProductItemToken
    :param token_list: 検索対象のOrderedProductItemTokenのリスト
    :return: 予約更新前後で等価となるOrderedProductItemToken。存在しない場合はNone
    """
    is_quantity_only = target_token.item.product_item.product.seat_stock_type.quantity_only
    for token in token_list:
        if is_quantity_only \
                and target_token.item.product_item.name == token.item.product_item.name \
                and target_token.serial == token.serial:
            return token  # 数受けの場合は「商品明細名」と「シリアル」で等価とみなす
        if not is_quantity_only \
                and target_token.item.product_item.name == token.item.product_item.name \
                and target_token.seat is not None and token.seat is not None \
                and target_token.seat.name == token.seat.name:
            return token  # 席ありの場合は「商品明細名」と「席名」で等価とみなす


def create_ts_option_from_token(token):
    """
    OrderedProductItemTokenからTSOptionを作成する。
    TSOptionはSkidataへ送信するチケットの付加情報。
    :param token: OrderedProductItemToken
    :return: TSOption
    """
    ordered_product_item = token.item
    ordered_product = ordered_product_item.ordered_product
    order = ordered_product.order

    product_item = ordered_product_item.product_item
    product = product_item.product
    sales_segment = product.sales_segment

    performance = product_item.performance
    start_on = performance.start_on
    event = performance.event
    organization = event.organization

    stock = product_item.stock
    stock_type = stock.stock_type

    # 販売区分グループプロパティ
    person_category_entry = SkidataPropertyEntry.find_entry_by_prop_type(
        sales_segment.sales_segment_group.id, SkidataPropertyTypeEnum.SalesSegmentGroup.v)
    # 商品明細プロパティ
    ticket_type_entry = SkidataPropertyEntry.find_entry_by_prop_type(
        product_item.id, SkidataPropertyTypeEnum.ProductItem.v)
    # Event ID は ORGコード + 公演の開演日時（YYYYmmddHHMM）
    skidata_event_id = u'{code}{start_date}'.format(code=organization.code,
                                                    start_date=start_on.strftime('%Y%m%d%H%M'))

    return TSOption(
        order_no=order.order_no,
        open_date=performance.open_on,
        start_date=start_on,
        stock_type=stock_type.name,
        product_name=product.name,
        product_item_name=product_item.name,
        gate=stock_type.attribute if stock_type else None,
        seat_name=token.seat.name if token.seat else None,
        sales_segment=sales_segment.name,
        ticket_type=ticket_type_entry.property.value if ticket_type_entry else None,
        person_category=person_category_entry.property.value if person_category_entry else None,
        event=skidata_event_id
    )


def find_equivalent_barcode(barcode_list, whitelist):
    """
    リストからWhitelistRecordと一致するSkidataBarcodeを取得する
    :param barcode_list: SkidataBarcodeのリスト
    :param whitelist: WhitelistRecord
    :return: WhitelistRecordと一致するSkidataBarcode, 見つからない場合はNone
    """
    for barcode in barcode_list:
        if whitelist.utid() == barcode.data:  # WhitelistRecord UTIDはQRコード
            return barcode
    return None


def send_whitelist_to_skidata(skidata_session, whitelist, barcode_list, fail_silently=False):
    """
    WhitelistをSkidataへ送信する。
    :param skidata_session: ISkidataSessionを提供するUtilityオブジェクト
    :param whitelist: WhitelistRecordまたはWhitelistRecordのリスト
    :param barcode_list: SkidataBarcodeリスト
    :param fail_silently: エラーの場合にExceptionをraiseしないかどうか
    """
    barcode_list_for_insert = []  # Skidataへ追加するQRコードを持つSkidataBarcodeのリスト
    for w in [whitelist] if isinstance(whitelist, WhitelistRecord) else whitelist:
        barcode = find_equivalent_barcode(barcode_list, w)
        if barcode is None:
            continue
        elif w.action() is TSAction.INSERT:
            barcode_list_for_insert.append(barcode)

    try:
        logger.debug(u'Sending Whitelist to Skidata because the performance starts today.')
        resp = skidata_session.send(whitelist=whitelist)
        logger.debug(u'Whitelist Import result: %s', resp.text)

        if resp.success:
            # 追加に成功した場合はsent_atを更新
            record_skidata_barcode_as_sent(barcode_list_for_insert)
        else:
            handle_whitelist_error(resp.errors, barcode_list)
            if not fail_silently:
                raise SkidataSendWhitelistError(u'Failed to import Whitelist to Skidata.')
    except SkidataWebServiceError as e:
        logger.error(e)
        logger.error('[SKI0003] Failed to import Whitelist to Skidata (SkidataBarcode ID: {}).'
                     .format(','.join([str(barcode.id) for barcode in barcode_list])))
        if not fail_silently:
            raise e


def handle_whitelist_error(hsh_error_list, barcode_list):
    """
    Skidata WebServiceのエラー要素を解析して該当のSkidataBarcodeを処理する
    Whitelist追加：
        Warningタイプのエラーの場合は該当のSkidataBarcode.sent_atを更新する

    :param hsh_error_list: altair.skidata.models.Errorのリスト
    :param barcode_list: SkidataBarcodeのリスト
    """
    # TODO エラー内容をエラーログテーブルに保存する
    barcode_list_for_insert = []  # sent_atを更新するSkidataBarcodeのリスト
    warning_barcode_id_list = []
    failure_barcode_id_list = []
    messages = []
    for error in hsh_error_list:
        error_type = error.type()
        if isinstance(error_type, HSHErrorType):
            error_type = error_type.value

        error_number = error.number()
        if isinstance(error_number, HSHErrorNumber):
            error_number = error_number.value

        msg = u'Error Type: {type}, Number: {number}, Description: {description}).' \
            .format(type=error_type, number=error_number, description=error.description())

        whitelist = error.whitelist()  # エラーが発生した Whitelist
        barcode = find_equivalent_barcode(barcode_list, whitelist)
        if barcode is not None:
            details = u'(SkidataBarcode ID: {}). {}'.format(barcode.id, msg)
        else:
            details = u'(QR: {}). {}'.format(whitelist.utid(), msg)

        if error.type() is HSHErrorType.WARNING:
            if barcode is not None:
                warning_barcode_id_list.append(str(barcode.id))
                if whitelist.action() is TSAction.INSERT:
                    # Warningの場合 Skidata に Whitelist は作成されたが、
                    # 何かエラーが発生したことを意味するので sent_at を更新します
                    barcode_list_for_insert.append(barcode)

            messages.append(u'Imported Whitelist to Skidata but '
                            u'something unexpected has occurred {}'.format(details))
        else:
            if barcode is not None:
                failure_barcode_id_list.append(str(barcode.id))
            messages.append(u'Failed to import Whitelist to Skidata {}'.format(details))

    record_skidata_barcode_as_sent(barcode_list_for_insert)

    error_msg = u'[SKI0003] Skidata WebService Error.'
    if warning_barcode_id_list:
        error_msg += ' Warning (SkidataBarcode ID: {})'.format(', '.join(warning_barcode_id_list))

    if failure_barcode_id_list:
        error_msg += ' Stop and Error (SkidataBarcode ID: {})'.format(', '.join(failure_barcode_id_list))
    logger.error('{} Details: \n{}'.format(error_msg, '\n'.join(messages)))


def record_skidata_barcode_as_sent(barcode_list):
    """
    SkidataBarcode.sent_atに現在時刻をセットする。
    :param barcode_list: SkidataBarcodeリスト
    """
    sent_at = datetime.now()
    for barcode in barcode_list:
        barcode.sent_at = sent_at
