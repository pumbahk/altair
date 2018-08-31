# -*- coding: utf-8 -*-
import codecs
import json
import sys
from pyramid.threadlocal import get_current_request
from altair.sqlahelper import get_db_session
from altair.app.ticketing.events.api import get_cms_data

from altair.app.ticketing.core.models import Event


def export_data(event_id):
    """
    altair_pshell_ticketingでこのメソッドをインポートして、
    対象イベントのIDを引数として入れて実行すれば、対象イベントのCMSデーターをJSONファイルで出力される。
    ファイルの出力箇所は'altair_pshell_ticketing'を起動する場所です。
    :param event_id:
    :return: None
    """
    request = get_current_request()
    db_session = get_db_session(request, 'slave')
    try:
        event = db_session.query(Event).filter_by(id=event_id).one()
    except:
        sys.exit(0)

    data = get_cms_data(request, event.organization, event)

    with codecs.open('data_{}.json'.format(event_id), 'w', "utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
