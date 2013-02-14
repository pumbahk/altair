# coding: utf-8
import logging
from altaircms.models import DBSession
from .receivedata import Scanner
from sqlalchemy.orm.exc import NoResultFound

from altaircms.auth.models import APIKey

class EventRepositry(object):
    def parse_and_save_event(self, request, parsed):       
        return parse_and_save_event(request, parsed)

def parse_and_save_event(request, parsed):
    # import pprint
    # pprint.pprint(parsed)
    return Scanner(DBSession, request)(parsed)

def validate_apikey(apikey):
    try:
        APIKey.query.filter_by(apikey=apikey).one()
    except NoResultFound:
        return False
    return True
