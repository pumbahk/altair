# -*- coding:utf-8 -*-

import transaction

from altaircms.page.models import (
    Page, PageSet
)
from altaircms.models import Category
def main(*args, **kwargs):
    ## slack off

    # for p in PageSet.query.all():
    #     print p.name
    Category.query.filter_by(name=u"チケットトップ").update({"pageset_id": PageSet.query.filter_by(name=u"トップページ ページセット").one().id}, synchronize_session="fetch")
    Category.query.filter_by(name=u"音楽").update({"pageset_id": PageSet.query.filter_by(name=u"音楽 ページセット").first().id}, synchronize_session="fetch")
    Category.query.filter_by(name=u"スポーツ").update({"pageset_id": PageSet.query.filter_by(name=u"スポーツ ページセット").one().id}, synchronize_session="fetch")
    Category.query.filter_by(name=u"演劇").update({"pageset_id": PageSet.query.filter_by(name=u"演劇 ページセット").one().id}, synchronize_session="fetch")
    Category.query.filter_by(name=u"イベント・その他").update({"pageset_id": PageSet.query.filter_by(name=u"イベント・その他 ページセット").one().id}, synchronize_session="fetch")
    transaction.commit()
