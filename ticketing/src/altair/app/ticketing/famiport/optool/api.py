from os import urandom
import hashlib
import six
from sqlalchemy.orm.exc import NoResultFound
from altair.sqlahelper import get_db_session
from .models import FamiPortOperator

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

