# -*- coding:utf-8 -*-

from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from altair.app.ticketing.users.models import Word
from sqlalchemy import desc


class WordBase(TicketingAdminResource):

    def __init__(self, request):
        self.session = get_db_session(request, name="slave")
        super(WordBase, self).__init__(request)


class WordResource(WordBase):

    def __init__(self, request):
        super(WordResource, self).__init__(request)

    def get_words(self):
        query = self.session.query(Word) \

        # if search_form and search_form.label.data:
        #     query = query.filter(ExternalSerialCodeSetting.label.like(u"%{0}%".format(search_form.label.data)))

        query = query.order_by(desc(Word.created_at))
        return query.all()
