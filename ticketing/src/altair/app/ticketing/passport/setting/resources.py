# -*- coding: utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session

from ..models import Passport, PassportNotAvailableTerm


class PassportResource(TicketingAdminResource):
    def __init__(self, request):
        super(PassportResource, self).__init__(request)

    @property
    def slave_session(self):
        return get_db_session(self.request, 'slave')

    @property
    def passport(self):
        passport_id = self.request.matchdict.get('passport_id', 0)
        return self.slave_session.query(Passport).filter(
            Passport.organization_id == self.user.organization_id).filter(Passport.id == passport_id).first()

    @property
    def passports(self):
        return self.slave_session.query(Passport).filter(Passport.organization_id == self.user.organization_id).all()

    @property
    def term(self):
        term_id = self.request.matchdict.get('term_id', 0)
        return self.slave_session.query(PassportNotAvailableTerm).join(Passport,
                                                                       Passport.id == PassportNotAvailableTerm.passport_id).filter(
            Passport.organization_id == self.user.organization_id).filter(
            PassportNotAvailableTerm.id == term_id).first()

    @property
    def terms(self):
        return self.slave_session.query(PassportNotAvailableTerm).join(Passport,
                                                                       Passport.id == PassportNotAvailableTerm.passport_id).filter(
            Passport.id == self.passport.id).filter(
            Passport.organization_id == self.user.organization_id).all()
