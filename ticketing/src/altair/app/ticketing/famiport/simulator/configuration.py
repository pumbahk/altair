from zope.interface import implementer, directlyProvides
from sqlalchemy.orm.exc import NoResultFound
from .interfaces import IFamiPortClientConfiguration, IFamiPortClientConfigurationRegistry
from ..models import FamiPortClient
from altair.sqlahelper import get_global_db_session

@implementer(IFamiPortClientConfigurationRegistry)
class FamiPortClientConfigurationRegistry(object):
    def __init__(self, registry):
        self.registry = registry

    def lookup(self, code):
        session = get_global_db_session(self.registry, 'famiport')
        try:
            client = session.query(FamiPortClient).filter_by(code=code).one()
            directlyProvides(client, IFamiPortClientConfiguration)
            return client
        except NoResultFound:
            return None
    
    def __iter__(self):
        session = get_global_db_session(self.registry, 'famiport')
        for client in session.query(FamiPortClient):
            directlyProvides(client, IFamiPortClientConfiguration)
            yield client

def includeme(config):
    config.registry.registerUtility(
        FamiPortClientConfigurationRegistry(config.registry),
        IFamiPortClientConfigurationRegistry
        )
