# -*- coding: utf-8 -*-
import logging

from .models import PointRedeem, PointStatusEnum
from .exceptions import PointAPIResponseParseException, PointRedeemNoFoundException
from xml.etree import ElementTree

logger = logging.getLogger(__name__)


def insert_point_redeem(point_api_response,
                        unique_id,
                        order_no,
                        group_id,
                        reason_id,
                        authed_at,
                        session=None):
    """
    PointRedeemテーブルへのInsert処理を実施します。
    :param point_api_response: ポイントAPIレスポンス
    :param unique_id: ポイントユニークID
    :param order_no: 予約番号
    :param group_id: ポイントグループID
    :param reason_id: ポイントリーズンID
    :param authed_at: authリクエスト発行時間
    :param session: DBセッション
    :return: PointRedeemテーブルの主キー
    """
    try:
        data_tree = get_element_tree(point_api_response)
        easy_id = get_point_element(data_tree, 'easy_id')
        auth_point = get_point_element(data_tree, 'secure_point')
    except Exception as e:
        logger.exception(e)
        logger.error('point_api_response=%s', point_api_response)
        raise PointAPIResponseParseException(
            '[PNT0002]failed to parse point API response. unique_id = {}'.format(unique_id))

    point_status = int(PointStatusEnum.auth)

    point_redeem = PointRedeem(
        easy_id=unicode(easy_id),
        unique_id=unique_id,
        order_no=unicode(order_no),
        group_id=group_id,
        reason_id=reason_id,
        point_status=point_status,
        auth_point=auth_point,
        authed_at=authed_at
    )
    return PointRedeem.create_point_redeem(point_redeem, session)


def update_point_redeem_for_fix(point_api_response,
                                unique_id,
                                fixed_at,
                                session=None):
    """
    ポイントAPIのFix処理時のPointRedeemテーブル更新を実施します。
    :param point_api_response: ポイントAPIレスポンス
    :param unique_id: ポイントユニークID
    :param fixed_at: fixリクエスト発行時間
    :param session: DBセッション
    """
    try:
        data_tree = get_element_tree(point_api_response)
        fix_point = get_point_element(data_tree, 'fix_point')
    except Exception as e:
        logger.exception(e)
        logger.error('point_api_response=%s', point_api_response)
        raise PointAPIResponseParseException(
            '[PNT0002]failed to parse point API response. unique_id = {}'.format(unique_id))

    point_status = int(PointStatusEnum.fix)

    point_redeem = PointRedeem.get_point_redeem(unique_id=unique_id, session=session)
    if point_redeem is None:
        raise PointRedeemNoFoundException('[PNT0004]PointRedeem record is not found. unique_id = {}'.format(unique_id))

    point_redeem.fix_point = fix_point
    point_redeem.point_status = point_status
    point_redeem.fixed_at = fixed_at

    PointRedeem.update_point_redeem(point_redeem, session)


def update_point_redeem_for_cancel(point_api_response,
                                   canceled_at,
                                   unique_id=None,
                                   order_no=None,
                                   session=None):
    """
    ポイントAPIのCancel処理時のPointRedeemテーブル更新を実施します。
    :param point_api_response: ポイントAPIレスポンス
    :param canceled_at: cancelリクエスト発行時間
    :param unique_id: ポイントユニークID
    :param order_no: 予約番号
    :param session: DBセッション
    """
    try:
        data_tree = get_element_tree(point_api_response)
        fix_point = get_point_element(data_tree, 'fix_point')
    except Exception as e:
        logger.exception(e)
        logger.error('point_api_response=%s', point_api_response)
        raise PointAPIResponseParseException('[PNT0003]failed to parse point API response.'
                                             ' unique_id = {}, order_no = {}'.format(unique_id, order_no))

    point_status = int(PointStatusEnum.cancel)

    if unique_id is not None:
        point_redeem = PointRedeem.get_point_redeem(unique_id=unique_id, session=session)
    else:
        point_redeem = PointRedeem.get_point_redeem(order_no=order_no, session=session)

    if point_redeem is None:
        raise PointRedeemNoFoundException('[PNT0005]PointRedeem record is not found. '
                                          ' unique_id = {}, order_no = {}'.format(unique_id, order_no))

    point_redeem.fix_point = fix_point
    point_redeem.point_status = point_status
    point_redeem.canceled_at = canceled_at

    PointRedeem.update_point_redeem(point_redeem, session)


def update_point_redeem_for_rollback(unique_id=None,
                                     order_no=None,
                                     session=None):
    """
    ポイントAPIのrollback処理時のPointRedeemテーブル更新を実施します。
    :param unique_id: ポイントユニークID
    :param order_no: 予約番号
    :param session: DBセッション
    """
    point_status = int(PointStatusEnum.rollback)

    if unique_id is not None:
        point_redeem = PointRedeem.get_point_redeem(unique_id=unique_id, session=session)
    else:
        point_redeem = PointRedeem.get_point_redeem(order_no=order_no, session=session)

    if point_redeem is None:
        raise PointRedeemNoFoundException('[PNT0005]PointRedeem record is not found.'
                                          ' unique_id = {}, order_no = {}'.format(unique_id, order_no))

    point_redeem.point_status = point_status

    PointRedeem.delete_point_redeem(point_redeem, session)


def update_point_redeem_for_payment_retry(point_api_response,
                                          point_redeem_record,
                                          unique_id,
                                          order_no,
                                          authed_at,
                                          session=None):
    """
    既存のPointRedeemレコードのunique_idを更新する
    :param point_api_response: ポイントAPIレスポンス
    :param unique_id: ポイントユニークID
    :param order_no: 予約番号
    :param authed_at: authリクエスト発行時間
    :param session: DBセッション
    :return: 更新レコードのprimary key
    """
    try:
        data_tree = get_element_tree(point_api_response)
        easy_id = get_point_element(data_tree, 'easy_id')
        auth_point = get_point_element(data_tree, 'secure_point')
    except Exception as e:
        logger.exception(e)
        logger.error('point_api_response=%s', point_api_response)
        raise PointAPIResponseParseException(
            '[PNT0002]failed to parse point API response. unique_id = {}'.format(unique_id))

    # 論理削除の解除
    point_redeem_record.deleted_at = None
    # レコードの更新 (group_id, reason_idは据え置き)
    point_redeem_record.unique_id = unique_id
    point_redeem_record.auth_point = auth_point
    point_redeem_record.easy_id = unicode(easy_id)
    point_redeem_record.point_status = int(PointStatusEnum.auth)
    point_redeem_record.authed_at = authed_at

    PointRedeem.update_point_redeem(point_redeem_record, include_deleted=True)
    return point_redeem_record.id


def get_result_code(point_api_response):
    """
    ポイントAPIのレスポンスから、存在する全てのresult_codeを取得します。※ result_code は複数存在することもあります。
    parseに失敗する可能性があるので、create_point_redeemメソッドを参考に例外のハンドリングを入れてください。
    :param point_api_response: ポイントAPIレスポンス
    :return: ポイントAPI result_code リスト
    """
    data_tree = get_element_tree(point_api_response)
    return [element.text for element in data_tree.findall('result_code')]


def get_unique_id(point_api_response):
    """
    ポイントAPIのレスポンスからunique_idを取得します。
    parseに失敗する可能性があるので、create_point_redeemメソッドを参考に例外のハンドリングを入れてください。
    :param point_api_response: ポイントAPIレスポンス
    :return: ポイントAPI unique_id
    """
    data_tree = get_element_tree(point_api_response)
    return get_point_element(data_tree, 'unique_id')


def get_element_tree(point_api_response):
    """
    ポイントAPIのレスポンスからdataタグ内の情報を取得します。
    :param point_api_response: ポイントAPIレスポンス
    :return: ポイントAPI dataタグ
    """
    result_tree = ElementTree.fromstring(point_api_response)
    return result_tree.find('data')


def get_point_element(data_tree, element_name):
    """
    ポイントAPI dataタグ内の指定した要素を取得します。
    :param data_tree: ポイントAPI dataタグ
    :param element_name: 要素名
    :return: 指定した要素の情報
    """
    return data_tree.find(element_name).text
