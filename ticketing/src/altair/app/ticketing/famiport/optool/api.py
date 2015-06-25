from os import urandom
import hashlib
import six
from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session
from .models import FamiPortOperator
from ..models import FamiPortPerformance, FamiPortEvent

def create_user(request, user_name, password, role):
    salt = u''.join('%02x' % six.byte2int(c) for c in urandom(16))
    h = hashlib.sha256()
    h.update(salt + password)
    password_digest = h.hexdigest()
    operator = FamiPortOperator(
        user_name=user_name,
        password=(salt + password_digest),
        role=role
        )
    session = get_db_session(request, 'famiport')
    session.add(operator)
    session.commit()

def lookup_user_by_credentials(request, user_name, password):
    session = get_db_session(request, 'famiport')
    try:
        operator = session.query(FamiPortOperator) \
            .filter(FamiPortOperator.user_name == user_name) \
            .one()
        h = hashlib.sha256()
        h.update(operator.password[0:32] + password)
        password_digest = h.hexdigest()
        if operator.password[32:] != password_digest:
            return None
        return operator
    except NoResultFound:
        return None

def lookup_user_by_id(request, id):
    session = get_db_session(request, 'famiport')
    try:
        return session.query(FamiPortOperator) \
            .filter(FamiPortOperator.id == id) \
            .one()
    except NoResultFound:
        return None

def lookup_performance_by_searchform_data(request, formdata=None):
    fami_session = get_db_session(request, name="famiport")

    query = fami_session.query(FamiPortPerformance) \
                        .join(FamiPortEvent, FamiPortPerformance.famiport_event_id == FamiPortEvent.id)

    if formdata.get('event_id'):
        query = query.filter(FamiPortEvent.id==formdata.get('event_id'))

    if formdata.get('event_code_1'):
        query = query.filter(FamiPortEvent.code_1==formdata.get('event_code_1').zfill(6))
        if formdata.get('event_code_2'):
            query = query.filter(FamiPortEvent.code_2==formdata.get('event_code_2').zfill(4))

    if formdata.get('event_name_1'):
        pattern = u'%{}%'.format(formdata.get('event_name_1'))
        query = query.filter(FamiPortEvent.name_1.like(pattern))

    if formdata.get('performance_name'):
        pattern = u'%{}%'.format(formdata.get('performance_name'))
        query = query.filter(FamiPortPerformance.name.like(pattern))

    if formdata.get('venue_name'):
        pattern = u'%{}%'.format(formdata.get('venue_name'))
        query = query.filter(FamiPortEvent.venue.like(pattern))

    if formdata.get('performance_from'):
        req_from = formdata.get('performance_from') + ' 00:00:00'
        if formdata.get('performance_to'):
            req_to = formdata.get('performance_to') + ' 23:59:59'
            query = query.filter(FamiPortPerformance.start_at >= req_from,
                                 FamiPortPerformance.start_at <= req_to)
        else:
            query = query.filter(FamiPortPerformance.start_at >= req_from)
    elif formdata.get('performance_to'):
        req_from = '1900-01-01 00:00:00'
        req_to = formdata.get('performance_to') + ' 23:59:59'
        query = query.filter(FamiPortPerformance.start_at >= req_from,
                             FamiPortPerformance.start_at <= req_to)

    performances = query.all()
    return performances

