# -*- coding:utf-8 -*-
from . models import NotifyUpdateTicketInfoTask


def delete_old_task_history(request, bundle_id, older_than=3):
    """
    チケット券面構成に紐づく古いタスク履歴を削除する
    :param request: リクエストオブジェクト
    :param bundle_id: チケット券面構成ID
    :param older_than: 削除するレコードのオフセット値
    :return:
    """
    result = NotifyUpdateTicketInfoTask.query.filter_by(
        ticket_bundle_id=bundle_id
    ).order_by(
        NotifyUpdateTicketInfoTask.id.desc()
    ).offset(older_than).all()

    for r in result:
        r.delete()

    return result
