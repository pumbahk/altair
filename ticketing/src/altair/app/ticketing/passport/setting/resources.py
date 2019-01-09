# -*- coding: utf-8 -*-
import os
import urllib

from altair.app.ticketing.core.models import Performance, Event
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from pyramid.response import FileResponse

from ..models import Passport, PassportNotAvailableTerm, PassportUser


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
    def origin_term(self):
        term_id = self.request.matchdict.get('term_id', 0)
        return PassportNotAvailableTerm.query.join(Passport,
                                                   Passport.id == PassportNotAvailableTerm.passport_id).filter(
            Passport.organization_id == self.user.organization_id).filter(
            PassportNotAvailableTerm.id == term_id).first()

    @property
    def terms(self):
        return self.slave_session.query(PassportNotAvailableTerm).join(Passport,
                                                                       Passport.id == PassportNotAvailableTerm.passport_id).filter(
            Passport.id == self.passport.id).filter(
            Passport.organization_id == self.user.organization_id).all()

    @property
    def passport_user(self):
        passport_user_id = self.request.matchdict.get('passport_user_id', 0)
        return self.slave_session.query(PassportUser).join(Passport, Passport.id == PassportUser.passport_id).filter(
            Passport.organization_id == self.user.organization_id).filter(
            PassportUser.id == passport_user_id).first()

    @property
    def passport_users(self):
        return self.slave_session.query(PassportUser).join(Passport, Passport.id == PassportUser.passport_id).filter(
            Passport.organization_id == self.user.organization_id).all()

    @property
    def performances(self):
        return Performance.query.join(Event, Event.id == Performance.event_id).filter(
            Event.organization_id == self.user.organization_id)

    def exist_passport_performance(self):
        return self.slave_session.query(Passport).filter(
            Passport.performance_id == self.request.POST['performance_id']).first()

    def save_passport(self, passport, form):
        params = form.data
        passport.name = params["name"]
        passport.available_day = params["available_day"]
        passport.performance_id = params["performance_id"]
        passport.daily_passport = params["daily_passport"]
        passport.is_valid = params["is_valid"]
        passport.organization_id = self.user.organization_id
        passport.save()

    def save_term(self, term, form):
        params = form.data
        term.start_on = params["start_on"]
        term.end_on = params["end_on"]
        origin_term = self.origin_term
        if not origin_term:
            term.passport_id = self.request.matchdict['passport_id']
        term.save()

    def passport_user_image_download(self):
        access_key = self.request.registry.settings["s3.access_key"]
        secret_key = self.request.registry.settings["s3.secret_key"]
        bucket_name = self.request.registry.settings["s3.bucket_name"]

        conn = S3Connection(access_key, secret_key)
        bucket = conn.get_bucket(bucket_name)

        s3key = Key(bucket)
        s3key.key = self.passport_user.image_path
        file_name = u"passport_user{0}.png".format(self.passport_user.id)
        file_path = "/tmp/{0}".format(file_name)

        f = open(file_path, 'w')
        s3key.get_file(f)

        response = FileResponse(os.path.abspath(file_path))
        response.headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', "attachment; filename*=utf-8''%s" % urllib.quote(file_name))
        ]
        os.remove(file_path)
        return response
