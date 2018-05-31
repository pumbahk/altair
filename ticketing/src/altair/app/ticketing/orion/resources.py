# -*- coding: utf-8 -*-

from altair.aes_urlsafe import AESURLSafe
from altair.sqlahelper import get_db_session

from altair.app.ticketing.resources import TicketingAdminResource


class OrionResource(TicketingAdminResource):
    def __init__(self, request):
        super(OrionResource, self).__init__(request)
        self.session = get_db_session(request, name="slave")


class OrionApiResource(OrionResource):
    def __init__(self, request):
        super(OrionApiResource, self).__init__(request)
        self.aes = AESURLSafe(key="ALTAIR_AES_ENCRYPTION_FOR_ORION!")

    def api_auth(self):
        x_app_key = self.request.headers.get('x-app-key')
        if not x_app_key:
            return False
        try:
            return self.aes.decrypt(x_app_key) == u'request_from_orion_server'
        except Exception:
            return False