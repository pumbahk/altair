# encoding: utf-8
import logging
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.sqlahelper import get_db_session
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import SalesSegment
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart.interfaces import ICartResource
from altair.app.ticketing.lots.interfaces import ILotResource
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
        return session.query(u_m.Membership).filter_by(organization_id=request.organization.id).all()

def do_authenticate(request, membership, username, password):
    """認証を行う。戻り値は認証に失敗したときはNoneで、
       成功したときは認証時に得られた何らかのメタデータなどをdictで。
       空のdictが返ることもあるので、is not None でチェックする必要がある"""
    session = get_db_session(request, 'slave')
    user_query = session.query(u_m.User) \
        .join(u_m.User.member).join(u_m.Member.membership) \
        .filter(u_m.Member.auth_identifier == username) \
        .filter(u_m.Member.auth_secret == password) \
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

def login_url(request):
    organization = cart_api.get_organization(request)
    url = request.route_url('fc_auth.login', membership=u'-')

    if ICartResource.providedBy(request.context):
        session = get_db_session(request, 'slave')
        source = None
        performance = None
        try:
            performance = request.context.performance
        except:
            pass
        if performance is not None:
            source = performance
        else:
            event = None
            try:
                event = request.context.event
            except:
                pass
            if event is not None:
                source = event
        if source is not None:
            logger.info("source=%r" % source)
            membership = source.query_sales_segments(type='all', now=request.context.now).join(SalesSegment.membergroups).join(u_m.MemberGroup.membership).with_entities(u_m.Membership).first()
            logger.info("membership=%s" % (membership and membership.name))
            if membership is not None:
                url = request.route_url('fc_auth.login', membership=membership.name)
    elif ILotResource.providedBy(request.context):
        session = get_db_session(request, 'slave')
        membership = session.query(u_m.Membership).join(u_m.MemberGroup.membership).join(u_m.MemberGroup_SalesSegment).filter(u_m.MemberGroup_SalesSegment.c.sales_segment_id == request.context.lot.sales_segment_id).first()
        logger.info("membership=%s" % (membership and membership.name))
        if membership is not None:
            url = request.route_url('fc_auth.login', membership=membership.name)

    logger.debug("login url %s" % url)
    return url 

