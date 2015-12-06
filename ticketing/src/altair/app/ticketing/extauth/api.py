from .interfaces import ICommunicator
from pyramid.interfaces import IRequest
from .models import Member
from altair.sqlahelper import get_db_session
from .utils import generate_salt, digest_secret

def get_communicator(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(ICommunicator)

def create_member(request, member_set, name, auth_identifier, auth_secret):
    salt = generate_salt()
    digest = digest_secret(auth_secret, salt)
    member = Member(
        member_set=member_set,
        name=name,
        auth_identifier=auth_identifier,
        auth_secret=digest
        )
    session = get_db_session(request, 'extauth')
    session.add(member)
    session.flush()
    return member

