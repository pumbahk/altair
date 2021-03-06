# -*- coding: utf-8 -*-
import logging
from datetime import datetime, date

from altair.app.ticketing.skidata.exceptions import SkidataSendWhitelistError
from altair.app.ticketing.skidata.models import SkidataBarcode, SkidataBarcodeErrorHistory
from altair.app.ticketing.orders.models import OrderedProductItemToken
from altair.app.ticketing.core.models import SeatAttribute
from altair.skidata.api import make_whitelist
from altair.skidata.exceptions import SkidataWebServiceError
from altair.skidata.interfaces import ISkidataSession
from altair.skidata.models import TSAction, TSOption, HSHErrorType, HSHErrorNumber, WhitelistRecord
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger(__name__)


def create_new_barcode(order_no):
    """
    指定した予約番号を元に、SkidataBarcodeデータを新規に生成する。
    :param order_no: 予約番号
    """
    opi_tokens = OrderedProductItemToken.find_all_by_order_no(order_no)
    for token in opi_tokens:
        SkidataBarcode.insert_new_barcode(token.id)


def send_whitelist_if_necessary(request, order, fail_silently=False):
    """
    指定した予約が支払済みで公演が今日開演、Skidata連携ONの設定、
    そしてSkidataBarcodeが未連携の場合はSkidataへWhitelistを送信する
    :param request: リクエスト
    :param order: Order
    :param fail_silently: エラーの場合にExceptionをraiseしないかどうか
    """
    performance = order.performance
    # 予約が支払済でキャンセルや払戻では無い状態で、
    # 公演が今日開演で公演のイベントの設定とORGの設定がSkidata連携ONの場合以外は対象外
    if not (order.paid_at is not None and performance.start_on.date() == date.today()
            and order.canceled_at is None and order.refund_id is None and order.refunded_at is None
            and performance.event.organization.setting.enable_skidata
            and performance.event.setting.enable_skidata):
        return

    whitelist = []
    barcode_list = []
    for barcode in SkidataBarcode.find_all_by_order_no(order.order_no):
        token = barcode.ordered_product_item_token
        if not (barcode.sent_at is None and barcode.canceled_at is None):
            continue
        # SkidataBarcode の sent_at と canceled_at が無い状態、つまり未連携の場合は
        # SkidataへWhitelistを送信するのでWhitelistRecordを作成する
        # Whitelistのexpireは公演の開演年の12月31日 23:59:59
        expire = datetime(year=performance.start_on.year, month=12, day=31, hour=23, minute=59, second=59)
        whitelist.append(
            make_whitelist(action=TSAction.INSERT, qr_code=barcode.data,
                           ts_option=create_ts_option_from_token(token), expire=expire)
        )
        barcode_list.append(barcode)

    skidata_session = request.registry.queryUtility(ISkidataSession)
    if whitelist and skidata_session is not None:
        logger.debug(u'Send Whitelist to Skidata because the performance starts today (SkidataBarcode ID: %s)',
                     ', '.join([str(barcode.id) for barcode in barcode_list]))
        send_whitelist_to_skidata(skidata_session, whitelist, barcode_list, fail_silently)


def delete_whitelist_if_necessary(request, order_no, fail_silently=False):
    """
    指定した予約番号のOrderedProductItemTokenに紐づくSkidataBarcodeのQRコードがWhitelistとして送信されている場合削除する
    :param request: リクエスト
    :param order_no: 予約番号
    :param fail_silently: エラーの場合にExceptionをraiseしないかどうか
    """
    whitelist = []
    barcode_list = []
    for barcode in SkidataBarcode.find_all_by_order_no(order_no):
        if barcode.sent_at is not None:
            whitelist.append(make_whitelist(action=TSAction.DELETE, qr_code=barcode.data))
            barcode_list.append(barcode)

    skidata_session = request.registry.queryUtility(ISkidataSession)
    if whitelist and skidata_session is not None:
        logger.debug('Delete Whitelist because it\'s already sent (SkidataBarcode ID: %s) ',
                     ', '.join([str(barcode.id) for barcode in barcode_list]))
        send_whitelist_to_skidata(skidata_session, whitelist, barcode_list, fail_silently)


def update_barcode_to_refresh_order(request, order_no, existing_barcode_list):
    """
    予約更新に伴うSkidataBarcode更新を実施する。
    指定した予約番号と、更新前のSkidataBarcodeのリストを元に予約更新によるSkidataBarcode.ordered_product_item_tokenの更新や、
    バーコードの追加・削除などを実施する。
    :param request: リクエスト
    :param order_no: 予約番号
    :param existing_barcode_list: 更新前の予約に紐づく既存のSkidataBarcodeリスト
    """
    barcode_and_token_to_update = list()  # 既存のSkidataBarcodeにひもづくOrderedProductItemTokenを更新するためのリスト
    barcode_list_to_cancel = list()  # 予約更新で削除されたWhitelist未送信のSkidataBarcodeを削除するためのリスト
    barcode_list_to_delete_whitelist = list()  # 予約更新で削除されたWhitelist送信済のSkidataBarcodeのリスト
    whitelist_to_delete = list()  # HSHから削除するためのWhitelistオブジェクトのリスト
    skidata_session = request.registry.queryUtility(ISkidataSession)
    tokens_to_add_barcode = list()  # 予約更新で追加されたOrderedProductItemTokenにSkidataBarcodeを追加するためのリスト

    new_opi_tokens = OrderedProductItemToken.find_all_by_order_no(order_no)
    for existing_barcode in existing_barcode_list:
        existing_token = existing_barcode.ordered_product_item_token
        equivalent_token = find_equivalent_token_from_list(existing_token, new_opi_tokens)
        if equivalent_token:
            barcode_and_token_to_update.append((existing_barcode, equivalent_token))
        elif existing_barcode.sent_at is None:  # キャンセル対象(予約更新後に存在しない)でWhitelist未送信
            barcode_list_to_cancel.append(existing_barcode)
        else:  # キャンセル対象(予約更新後に存在しない)でWhitelist送信済
            barcode_list_to_delete_whitelist.append(SkidataBarcode.find_by_barcode(existing_barcode.data))
            whitelist_to_delete.append(make_whitelist(action=TSAction.DELETE, qr_code=existing_barcode.data))

    tokens_to_update_barcode = [token for _, token in barcode_and_token_to_update]
    for new_token in new_opi_tokens:
        if new_token not in tokens_to_update_barcode:  # 更新リストにない場合は、追加とみなす(商品明細追加や商品個数追加など)
            tokens_to_add_barcode.append(new_token)

    for barcode, token in barcode_and_token_to_update:  # SkidataBarcodeのordered_product_item_tokenの置き換え
        SkidataBarcode.update_token(barcode.id, token.id)
    for barcode in barcode_list_to_cancel:  # 予約更新後に存在しないWhitelist未送信のバーコードをキャンセル
        SkidataBarcode.cancel(barcode.id)
    for token in tokens_to_add_barcode:  # 予約更新後に追加されたOrderedProductItemTokenにバーコードを付与
        SkidataBarcode.insert_new_barcode(token.id)
    if whitelist_to_delete and skidata_session is not None:
        logger.debug('Delete Whitelist because it\'s already sent (SkidataBarcode ID: %s) ',
                     ', '.join([str(barcode.id) for barcode in barcode_list_to_delete_whitelist]))
        send_whitelist_to_skidata(skidata_session, whitelist_to_delete, barcode_list_to_delete_whitelist,
                                  fail_silently=False)


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
    sales_segment_group_property = sales_segment.sales_segment_group.skidata_property
    # 商品明細プロパティ
    product_item_property = product_item.skidata_property
    # Event ID は ORGコード + 公演の開演日時（YYYYmmddHHMM）
    skidata_event_id = u'{code}{start_date}'.format(code=organization.code,
                                                    start_date=start_on.strftime('%Y%m%d%H%M'))

    # TKT10677_インナー発券の場合gateが反映されてない対応
    gate=stock_type.attribute if stock_type else None
    if token.seat:
        seat_attribute_gate=SeatAttribute.query\
            .filter(SeatAttribute.seat_id==token.seat_id)\
            .filter(SeatAttribute.name=='gate').first()
        if seat_attribute_gate:
            gate=seat_attribute_gate.value

    return TSOption(
        order_no=order.order_no,
        open_date=performance.open_on,
        start_date=start_on,
        stock_type=stock_type.name,
        product_name=product.name,
        product_item_name=product_item.name,
        gate=gate,
        seat_name=token.seat.name if token.seat else None,
        sales_segment=sales_segment.name,
        ticket_type=sales_segment_group_property.value if sales_segment_group_property else None,
        person_category=product_item_property.value if product_item_property else None,
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
    Skidataへ追加したWhitelist（Warningエラーを含む）のQRコードに一致するSkidataBarcodeのsent_atを更新。
    Skidataから削除したWhitelist（Warningエラーを含む）のQRコードに一致するSkidataBarcodeのcanceled_atを更新。
    :param skidata_session: ISkidataSessionを提供するUtilityオブジェクト
    :param whitelist: WhitelistRecordまたはWhitelistRecordのリスト
    :param barcode_list: SkidataBarcodeリスト
    :param fail_silently: エラーの場合にExceptionをraiseしないかどうか
    """
    barcode_list_for_insert = []  # Skidataへ追加するQRコードを持つSkidataBarcodeのリスト
    barcode_list_for_delete = []  # Skidataから削除するQRコードを持つSkidataBarcodeのリスト
    for w in [whitelist] if isinstance(whitelist, WhitelistRecord) else whitelist:
        barcode = find_equivalent_barcode(barcode_list, w)
        if barcode is None:
            continue
        elif w.action() is TSAction.INSERT:
            barcode_list_for_insert.append(barcode)
        elif w.action() is TSAction.DELETE:
            barcode_list_for_delete.append(barcode)

    try:
        resp = skidata_session.send(whitelist=whitelist)
        logger.debug(u'Whitelist Import result: %s', resp.text)

        if resp.success:
            # 追加に成功した場合はsent_atを更新
            record_skidata_barcode_as_sent(barcode_list_for_insert)
            # 削除に成功した場合はcanceled_atを更新
            record_skidata_barcode_as_canceled(barcode_list_for_delete)
        else:
            handle_whitelist_error(hsh_error_list=resp.errors,
                                   barcode_list_for_insert=barcode_list_for_insert,
                                   barcode_list_for_delete=barcode_list_for_delete,
                                   fail_silently=fail_silently)
    except SkidataWebServiceError as e:
        logger.error(e)
        logger.error('[SKI0003] Failed to import Whitelist to Skidata (SkidataBarcode ID: {}).'
                     .format(','.join([str(barcode.id) for barcode in barcode_list])))
        if not fail_silently:
            raise e


def handle_whitelist_error(hsh_error_list,
                           barcode_list_for_insert=None,
                           barcode_list_for_delete=None,
                           fail_silently=False):
    """
    Skidata WebServiceのWhitelistリクエストに対するエラー要素を解析して以下の処理を行う。
    - SkidataBarcodeのQRコードに一致するWhitelist連携エラー内容をSkidataBarcodeErrorHistoryへ記録。
    - fail_silentlyがTrueの場合：
        Skidataへ追加したWhitelist（Warningエラーを含む）のQRコードに一致するSkidataBarcodeのsent_atを更新。
        Skidataから削除したWhitelist（Warningエラーを含む）のQRコードに一致するSkidataBarcodeのcanceled_atを更新。

    :param hsh_error_list: altair.skidata.models.Errorのリスト
    :param barcode_list_for_insert: Skidataへ追加するQRコードを持つSkidataBarcodeのリスト。
                                    インポート結果が成功かWarningの場合は sent_at を更新する
    :param barcode_list_for_delete: Skidataから削除するQRコードを持つSkidataBarcodeのリスト
                                    インポート結果が成功かWarningの場合は canceled_at を更新する
    :param fail_silently: エラーの場合にExceptionをraiseしないかどうか
    """
    if barcode_list_for_insert is None:
        barcode_list_for_insert = []
    if barcode_list_for_delete is None:
        barcode_list_for_delete = []

    warning_barcode_id_list = []
    failure_barcode_id_list = []
    messages = []
    # SkidataBarcodeErrorHistory にエラーを記録する際に使用するセッション。
    # ロールバックしないように autocommit の別セッションにします。
    barcode_error_session = scoped_session(sessionmaker(autocommit=True))
    stop = False
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
        # Whitelistインポート以外でエラーが発生した場合にはError要素にWhitelistRecordはありません。
        # またStopタイプのエラーはインポート処理全てが失敗したことを意味します。
        if whitelist is None or error.type() is HSHErrorType.STOP:
            messages.append('Failed to import all Whitelist to Skidata '
                            'as a critical error has occurred. {}'.format(msg))
            stop = True
            break

        barcode = None
        if whitelist.action() is TSAction.INSERT:
            barcode = find_equivalent_barcode(barcode_list_for_insert, whitelist)
        elif whitelist.action() is TSAction.DELETE:
            barcode = find_equivalent_barcode(barcode_list_for_delete, whitelist)

        details = u'(SkidataBarcode ID: {}). {}'.format(barcode.id, msg) \
            if barcode is not None else u'(QR: {}). {}'.format(whitelist.utid(), msg)

        if error.type() is HSHErrorType.WARNING:
            # Warningはインポート自体はできたが、局所的なエラーが発生したことを意味するので成功とみなします
            # 追加の場合：Whitelist自体は登録できたがTSProperty等の要素を全て登録できなかった or 既にWhitelistが存在している
            # 削除の場合：削除する Whitelist データが見つからない
            if barcode is not None:
                warning_barcode_id_list.append(str(barcode.id))
            messages.append(u'Imported Whitelist to Skidata but '
                            u'something unexpected has occurred {}'.format(details))
        else:
            if barcode is not None:
                failure_barcode_id_list.append(str(barcode.id))
                # Warning以外のエラー（Error, STOP）はインポート失敗なので更新対象から除く
                if whitelist.action() is TSAction.INSERT:
                    barcode_list_for_insert.remove(barcode)
                elif whitelist.action() is TSAction.DELETE:
                    barcode_list_for_delete.remove(barcode)
            messages.append(u'Failed to import Whitelist to Skidata {}'.format(details))

        if barcode is not None:  # SkidataBarcode 連携エラーを記録する
            SkidataBarcodeErrorHistory.insert_new_history(skidata_barcode_id=barcode.id,
                                                          hsh_error_type=error.type(),
                                                          hsh_error_number=error.number(),
                                                          description=error.description(),
                                                          session=barcode_error_session)

    error_msg = u'[SKI0003] Skidata WebService Error.'
    if warning_barcode_id_list:
        error_msg += ' Warning (SkidataBarcode ID: {})'.format(', '.join(warning_barcode_id_list))

    if failure_barcode_id_list:
        error_msg += ' Error (SkidataBarcode ID: {})'.format(', '.join(failure_barcode_id_list))
    logger.error('{} Details: \n{}'.format(error_msg, '\n'.join(messages)))

    # fail_silently が偽の場合はraise
    if not fail_silently:
        raise SkidataSendWhitelistError(u'Failed to import Whitelist to Skidata.')

    # インポート処理が全て失敗していない場合は、更新対象のSkidataBarcodeリストのデータを更新する
    if not stop:
        record_skidata_barcode_as_sent(barcode_list_for_insert)
        record_skidata_barcode_as_canceled(barcode_list_for_delete)


def record_skidata_barcode_as_sent(barcode_list):
    """
    SkidataBarcode.sent_atに現在時刻をセットする。
    :param barcode_list: SkidataBarcodeリスト
    """
    sent_at = datetime.now()
    for barcode in barcode_list:
        barcode.sent_at = sent_at


def record_skidata_barcode_as_canceled(barcode_list):
    """
    SkidataBarcode.canceled_atに現在時刻をセットする。
    :param
    barcode_list: SkidataBarcodeリスト
    """
    canceled_at = datetime.now()
    for barcode in barcode_list:
        barcode.canceled_at = canceled_at
