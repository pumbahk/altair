# -*- coding:utf-8 -*-
from pyramid.interfaces import IRequest
from .interfaces import IPointAPICommunicatorFactory


def get_stdonly(request, easy_id, org):
    """
    現在のユーザの保有ポイントを取得する
    :param request: リクエスト
    :param easy_id: 楽天会員ID
    :param org: organization code
    :return: ポイントAPIのレスポンスXML
    """
    point_api_client = create_point_api_communicator(request, org)

    # get-stdonlyリクエスト
    result = point_api_client.request_get_stdonly(easy_id)
    return result


def auth_stdonly(request, easy_id, auth_point, req_time, org):
    """
    ポイント充当の確保を行います。
    ※　req_timeはauth_stdonly, fixで同じ時間を使い回してください。(確保と確定は同時に実施するため)
    :param request: リクエスト
    :param easy_id: 楽天会員ID
    :param auth_point: 充当ポイント
    :param req_time: リクエスト発行時間
    :param org: organization code
    :return: ポイントAPIのレスポンスXML
    """
    point_api_client = create_point_api_communicator(request, org)

    # auth-stdonlyリクエスト
    result = point_api_client.request_auth_stdonly(easy_id, auth_point, req_time)
    return result


def fix(request, easy_id, fix_point, unique_id, fix_id, group_id, reason_id, req_time):
    """
    auth_stdonlyで確保したポイントをFixします。
    購入処理時に, auth_stdonly -> fix で同時にリクエストを行います。
    req_timeはauth_stdonlyで指定したものと同じ時間にしてください。
    :param request: リクエスト
    :param easy_id: 楽天会員ID
    :param fix_point: 承認要求ポイント
    :param unique_id: ユニークID
    :param fix_id: 承認する際に必要となるID(予約番号を指定してください)
    :param group_id: グループID
    :param reason_id: リーズンID
    :param req_time: リクエスト発行時間(※auth_stdonlyで送ったreq_timeと同じ時間で指定してください。)
    :return: ポイントAPIのレスポンスXML
    """
    point_api_client = create_point_api_communicator(request, None, group_id, reason_id)

    # fixリクエスト
    result = point_api_client.request_fix(easy_id, fix_point, unique_id, fix_id, req_time)
    return result


def cancel(request, easy_id, unique_id, fix_id, group_id, reason_id, req_time):
    """
    fixしたポイントをキャンセルします。
    :param request: リクエスト
    :param easy_id: 楽天会員ID
    :param unique_id: ユニークID
    :param fix_id: 承認する際に必要となるID(予約番号を指定してください)
    :param group_id: グループID
    :param reason_id: リーズンID
    :param req_time: リクエスト発行時間
    :return: ポイントAPIのレスポンスXML
    """
    # キャンセルを行う際は fix APIに fix_point = -1 でリクエストを送る
    fix_point = '-1'

    # fix時にfix_idは予約番号を指定しているため, キャンセル時にそのまま使用すると重複エラーになるので書き換えます
    fix_id = str(fix_id) + '_C'

    # fixメソッドを呼び出す
    result = fix(request, easy_id, fix_point, unique_id, fix_id, group_id, reason_id, req_time)
    return result


def rollback(request, easy_id, unique_id, group_id, reason_id):
    """
    確保, または確定したポイント充当のロールバックをします。
    ※ ロールバックしたデータはポイント利用履歴に表示されなくなります。
    主に充当処理以外の処理起因のエラー等でポイントのキャンセルを行いたい場合に利用してください。
    正常パターンでの充当キャンセルを実施する場合はcancelメソッドを利用してください。
    :param request: リクエスト
    :param easy_id: 楽天会員ID
    :param unique_id: ユニークID
    :param group_id: グループID
    :param reason_id: リーズンID
    :return: ポイントAPIのレスポンスXML
    """
    point_api_client = create_point_api_communicator(request, None, group_id, reason_id)

    # rollback リクエスト
    result = point_api_client.request_rollback(easy_id, unique_id)
    return result


def create_point_api_communicator(request_or_registry, org, group_id=None, reason_id=None):
    """
    ポイントAPIクライアントを呼び出す通信用クラスの初期化処理を行います。
    :param request_or_registry: リクエスト
    :param org: organization code
    :param group_id: グループID
    :param reason_id: リーズンID
    :return: PointAPICommunicatorFactory
    """
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    factory = registry.getUtility(IPointAPICommunicatorFactory)
    return factory(org, group_id, reason_id)
