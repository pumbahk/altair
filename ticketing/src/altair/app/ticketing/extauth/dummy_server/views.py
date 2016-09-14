import logging
from datetime import datetime
from pyramid.view import view_defaults, view_config
from pyramid.decorator import reify
from sqlalchemy import orm
import sqlalchemy as sa
from .models import EaglesUser, EaglesMembership, VisselUser, VisselMembership
from .interfaces import IRequestHandler
from .exceptions import BadRequestError

logger = logging.getLogger(__name__)


def _eagles_user_profile(self):
    handler = self.get_request_handler('check_memberships')
    params = handler.handle_request(self.request)
    openid_claimed_id = params['openid_claimed_id']
    include_permanent_memberships = params['include_permanent_memberships']
    user = self.request.sa_session.query(EaglesUser) \
        .filter(EaglesUser.openid_claimed_id == openid_claimed_id) \
        .one()
    cond = sa.and_(
        (EaglesMembership.valid_since == None) \
        | (EaglesMembership.valid_since <= datetime(params['start_year'], 1, 1)),
        (EaglesMembership.expire_at == None) \
        | (EaglesMembership.expire_at >= datetime(params['end_year'] + 1, 1, 1))
        )
    if not include_permanent_memberships:
        cond = sa.and_(
            cond,
            (EaglesMembership.valid_since != None) | (EaglesMembership.expire_at != None)
            )
    memberships = self.request.sa_session.query(EaglesMembership) \
        .filter(EaglesMembership.user_id == user.id) \
        .filter(cond) \
        .all()
    return handler.build_response(
        self.request,
        flavor='json',
        successful=True,
        value=memberships
        )

def _vissel_user_profile(self):
    handler = self.get_request_handler('check_memberships')
    params = handler.handle_request(self.request)
    openid_claimed_id = params['openid_claimed_id']
    include_permanent_memberships = params['include_permanent_memberships']
    user = self.request.sa_session.query(VisselUser) \
        .filter(VisselUser.openid_claimed_id == openid_claimed_id) \
        .one()
    cond = sa.and_(
        (VisselMembership.valid_since == None) \
        | (VisselMembership.valid_since <= datetime(params['start_year'], 1, 1)),
        (VisselMembership.expire_at == None) \
        | (VisselMembership.expire_at >= datetime(params['end_year'] + 1, 1, 1))
        )
    if not include_permanent_memberships:
        cond = sa.and_(
            cond,
            (VisselMembership.valid_since != None) | (VisselMembership.expire_at != None)
            )
    memberships = self.request.sa_session.query(VisselMembership) \
        .filter(VisselMembership.user_id == user.id) \
        .filter(cond) \
        .all()
    return handler.build_response(
        self.request,
        flavor='json',
        successful=True,
        value=memberships
        )

@view_defaults(renderer='json')
class ExtauthCheckMembershipAPI(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_request_handler(self, type):
        return self.request.registry.queryUtility(IRequestHandler, name=type)

    @view_config(route_name='extauth_dummy.check_memberships', context=orm.exc.NoResultFound)
    def no_result_found(self):
        handler = self.get_request_handler('check_memberships')
        response = handler.build_response(
            self.request,
            flavor='json',
            successful=True,
            value=None
            )
        response.status = 200
        return response

    @view_config(route_name='extauth_dummy.check_memberships', context=BadRequestError)
    def bad_request(self):
        handler = self.get_request_handler('check_memberships')
        response = handler.build_response(
            self.request,
            flavor='json',
            successful=False,
            value=self.context.message
            )
        response.status = 400
        return response

    @view_config(route_name='extauth_dummy.check_memberships')
    def user_profile(self):
        port = self.request.environ['SERVER_PORT']
        if port == '8044':
            response = _eagles_user_profile(self)
        elif port == '8045':
            response = _vissel_user_profile(self)

        return response

