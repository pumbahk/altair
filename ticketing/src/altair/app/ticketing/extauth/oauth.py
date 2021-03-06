import logging
from altair.sqlahelper import get_db_session
from pyramid.threadlocal import get_current_request
from sqlalchemy.orm.exc import NoResultFound
from .models import OAuthClient

logger = logging.getLogger(__name__)

class ClientRepository(object):
    def lookup(self, client_id, now):
        dbsession = get_db_session(get_current_request(), 'extauth_slave')
        client = None
        try:
            client = dbsession.query(OAuthClient).filter_by(client_id=client_id).one()
        except NoResultFound:
            pass
        return client
