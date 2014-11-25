# encoding: utf-8
import logging
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.sqlahelper import get_db_session
from altair.app.ticketing.users.models import Membership
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.cart import api as cart_api
import altair.app.ticketing.users.models as u_m
import altair.app.ticketing.core.models as c_m

logger = logging.getLogger(__name__)

def get_memberships(request, session=None):
    if session is None:
        session = DBSession
    if hasattr(request, 'context') and hasattr(request.context, 'memberships'):
        logger.info('memberships retrieved from context')
        return request.context.memberships
    else:
        logger.info('memberships retrieved directly')
        return session.query(Membership).filter_by(organization_id=request.organization.id).all()

def do_authenticate(request, membership, username, password):
    """認証を行う。戻り値は認証に失敗したときはNoneで、
       成功したときは認証時に得られた何らかのメタデータなどをdictで。
       空のdictが返ることもあるので、is not None でチェックする必要がある"""
    session = get_db_session(request, 'slave')
    user_query = session.query(u_m.User) \
        .filter(u_m.User.id == u_m.UserCredential.user_id) \
        .filter(u_m.Membership.id == u_m.UserCredential.membership_id) \
        .filter(u_m.UserCredential.auth_identifier == username) \
        .filter(u_m.UserCredential.auth_secret == password) \
        .filter(u_m.Membership.name == membership)
    try:
        user = user_query.one()
    except NoResultFound:
        logger.debug('no user found for user: %s' % username)
        return None
    except MultipleResultsFound:
        logger.error('multiple records found for user: %s' % username)
        return None
    return { 'user_id': user.id }

def login_url(request, event_id=None):
    organization = cart_api.get_organization(request)
    url = request.route_url('fc_auth.login', membership=organization.short_name)

    # EventIDから、会員種別を辿り、それが、Organizationのショートネームと違う場合、第二の会員種別として扱う。
    if event_id:
        session = get_db_session(request, 'slave')
        salessegment_group = session.query(c_m.SalesSegmentGroup) \
            .filter(c_m.SalesSegmentGroup.event_id==event_id).first()

        if salessegment_group:
            if len(salessegment_group.membergroups) > 0:
                membership = salessegment_group.membergroups[0].membership
                if organization.short_name != membership.name:
                    url = request.route_url('fc_auth.fixed.login', membership=membership.name)

    logger.debug("login url %s" % url)
    return url 

