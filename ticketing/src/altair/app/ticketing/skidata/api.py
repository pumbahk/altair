# -*- coding: utf-8 -*-

from altair.app.ticketing.skidata.models import SkidataBarcode
from altair.app.ticketing.orders.models import OrderedProductItemToken


def create_new_barcode(order_no):
    """
    指定した予約番号を元に、SkidataBarcodeデータを新規に生成する
    :param order_no: 予約番号
    """
    # TODO 試合当日はSKIDATAと連携
    opi_tokens = OrderedProductItemToken.find_all_by_order_no(order_no)
    for token in opi_tokens:
        SkidataBarcode.insert_new_barcode(token.id)


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
