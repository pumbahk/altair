# -*- coding:utf-8 -*-
from altaircms.page.models import PageSet, Page
from altaircms.models import _GenrePath
import sqlalchemy as sa

class SnsUtils(object):
    def __init__(self, request):
        self.request = request

    def get_sns_url(self, event_id):
        url = "http://ticket.rakuten.co.jp/"
        pageset = self.request.allowable(PageSet)\
            .filter(PageSet.event_id == event_id).first()
        if pageset:
            url = url + pageset.url
        return url

    def get_sns_url_from_genre(self, genre):
        url = "http://ticket.rakuten.co.jp/"
        genre_path = self.request.allowable(_GenrePath)\
            .filter(_GenrePath.genre_id == genre.id)\
            .order_by(sa.asc(_GenrePath.hop)).all()
        for path in genre_path:
            if not path.next_genre.is_root:
                url = url + path.next_genre.name + "/"
        url = url + genre.name
        return url

    def get_sns_title(self, event_id):
        title = u"楽天チケット"
        page = self.request.allowable(Page)\
            .join(PageSet, Page.pageset_id == PageSet.id)\
            .filter(PageSet.event_id == event_id)\
            .filter(Page.published == True).first()
        if page:
            title = page.name
        return title
