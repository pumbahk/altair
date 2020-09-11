# -*- coding:utf-8 -*-

from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session


class WordBase(TicketingAdminResource):

    def __init__(self, request):
        self.session = get_db_session(request, name="slave")
        super(WordBase, self).__init__(request)


class WordResource(WordBase):

    def __init__(self, request):
        super(WordResource, self).__init__(request)
