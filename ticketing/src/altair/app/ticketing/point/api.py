# -*- coding: utf-8 -*-

from .models import PointRedeem, PointStatusEnum
from xml.etree import ElementTree


def create_point_redeem(point_api_response,
                        unique_id,
                        order_id,
                        order_no,
                        group_id,
                        reason_id,
                        authed_at):
    """
    PointRedeemテーブルへのInsert処理を実施します。
    :param point_api_response: ポイントAPIレスポンス
    :param unique_id: ポイントユニークID
    :param order_id: Orderテーブルの主キー
    :param order_no: 予約番号
    :param group_id: ポイントグループID
    :param reason_id: ポイントリーズンID
    :param authed_at: authリクエスト発行時間
    :return: PointRedeemテーブルの主キー
    """
    data_tree = get_element_tree(point_api_response)
    easy_id = get_point_element(data_tree, 'easy_id')
    auth_point = get_point_element(data_tree, 'secure_point')
    point_status = int(PointStatusEnum.auth)

    point_redeem = PointRedeem(
        easy_id=unicode(easy_id),
        unique_id=unique_id,
        order_id=order_id,
        order_no=unicode(order_no),
        group_id=group_id,
        reason_id=reason_id,
        point_status=point_status,
        auth_point=auth_point,
        authed_at=authed_at
    )
    return PointRedeem.create_point_redeem(point_redeem)


def fix_point_redeem(point_api_response,
                     unique_id,
                     fixed_at):
    """
    ポイントAPIのFix処理時のPointRedeemテーブル更新を実施します。
    :param point_api_response: ポイントAPIレスポンス
    :param unique_id: ポイントユニークID
    :param fixed_at: fixリクエスト発行時間
    """
    data_tree = get_element_tree(point_api_response)
    fix_point = get_point_element(data_tree, 'fix_point')
    point_status = int(PointStatusEnum.fix)

    point_redeem = PointRedeem.get_point_redeem(unique_id=unique_id)

    point_redeem.fix_point = fix_point
    point_redeem.point_status = point_status
    point_redeem.fixed_at = fixed_at

    PointRedeem.update_point_redeem(point_redeem)


def cancel_point_redeem(point_api_response,
                        canceled_at,
                        unique_id=None,
                        order_id=None,
                        order_no=None):
    """
    ポイントAPIのCancel処理時のPointRedeemテーブル更新を実施します。
    :param point_api_response: ポイントAPIレスポンス
    :param canceled_at: cancelリクエスト発行時間
    :param unique_id: ポイントユニークID
    :param order_id: Orderテーブルの主キー
    :param order_no: 予約番号
    """
    data_tree = get_element_tree(point_api_response)
    fix_point = get_point_element(data_tree, 'fix_point')
    point_status = int(PointStatusEnum.cancel)

    if unique_id is not None:
        point_redeem = PointRedeem.get_point_redeem(unique_id=unique_id)
    elif order_id is not None:
        point_redeem = PointRedeem.get_point_redeem(order_id=order_id)
    else:
        point_redeem = PointRedeem.get_point_redeem(order_no=order_no)

    point_redeem.fix_point = fix_point
    point_redeem.point_status = point_status
    point_redeem.canceled_at = canceled_at

    PointRedeem.update_point_redeem(point_redeem)


def rollback_point_redeem(unique_id=None,
                          order_id=None,
                          order_no=None):
    """
    ポイントAPIのrollback処理時のPointRedeemテーブル更新を実施します。
    :param unique_id: ポイントユニークID
    :param order_id: Orderテーブルの主キー
    :param order_no: 予約番号
    """
    point_status = int(PointStatusEnum.rollback)

    if unique_id is not None:
        point_redeem = PointRedeem.get_point_redeem(unique_id=unique_id)
    elif order_id is not None:
        point_redeem = PointRedeem.get_point_redeem(order_id=order_id)
    else:
        point_redeem = PointRedeem.get_point_redeem(order_no=order_no)

    point_redeem.point_status = point_status

    PointRedeem.delete_point_redeem(point_redeem)


def get_result_code(point_api_response):
    """
    ポイントAPIのレスポンスからresult_codeを取得します。
    :param point_api_response: ポイントAPIレスポンス
    :return: ポイントAPI result_code
    """
    data_tree = get_element_tree(point_api_response)
    return get_point_element(data_tree, 'result_code')


def get_unique_id(point_api_response):
    """
    ポイントAPIのレスポンスからunique_idを取得します。
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
