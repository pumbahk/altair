# encoding: utf-8

import logging

from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session

logger = logging.getLogger(__name__)


class DiscountCodeSettingResource(TicketingAdminResource):

    def __init__(self, request):
        super(DiscountCodeSettingResource, self).__init__(request)

        self.request = request
        self.session = get_db_session(request, name="slave")

        self._make_empty_first_4_digits_if_needed()
        self._upper_following_2to4_digits()

    def _upper_following_2to4_digits(self):
        """POSTされたパラメータを大文字に変更"""
        if 'following_2to4_digits' in self.request.POST:
            self.request.POST['following_2to4_digits'] = self.request.POST['following_2to4_digits'].upper()

    def _make_empty_first_4_digits_if_needed(self):
        """コード管理元が自社でなければ頭4文字は空にする"""
        if 'issued_by' in self.request.POST:
            if self.request.POST['issued_by'] != 'own':
                self.request.POST['first_digit'] = u''
                self.request.POST['following_2to4_digits'] = u''


class DiscountCodeCodesResource(TicketingAdminResource):
    def __init__(self, request):
        super(DiscountCodeCodesResource, self).__init__(request)

        self.request = request
        self.session = get_db_session(request, name="slave")
