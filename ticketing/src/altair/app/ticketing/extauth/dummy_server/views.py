from datetime import datetime
from pyramid.view import view_defaults, view_config
from pyramid.decorator import reify
from sqlalchemy import orm
import sqlalchemy as sa
from .models import EaglesUser, EaglesMembership
from .interfaces import IRequestHandler
from .exceptions import BadRequestError

@view_defaults(renderer='json')
class EaglesExtauthCheckMembershipAPI(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_request_handler(self, type):
        return self.request.registry.queryUtility(IRequestHandler, name=type)

    @view_config(route_name='eagles_extauth.check_memberships', context=orm.exc.NoResultFound)
    def no_result_found(self):
        handler = self.get_request_handler('check_memberships')
        response = handler.build_response(
            self.request,
            flavor='json',
            successful=False,
            value=u'user not found'
            )
        response.status = 404
        return response

    @view_config(route_name='eagles_extauth.check_memberships', context=BadRequestError)
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

    @view_config(route_name='eagles_extauth.check_memberships')
    def user_profile(self):
        handler = self.get_request_handler('check_memberships')
        params = handler.handle_request(self.request)
        openid_claimed_id = params['openid_claimed_id']
        user = self.request.sa_session.query(EaglesUser) \
            .filter(EaglesUser.openid_claimed_id == openid_claimed_id) \
            .one()
        memberships = self.request.sa_session.query(EaglesMembership) \
            .filter(EaglesMembership.user_id == user.id) \
            .filter(
                sa.and_(
                    (EaglesMembership.valid_since == None) \
                    | sa.and_(EaglesMembership.valid_since >= datetime(params['start_year'], 1, 1),
                           EaglesMembership.valid_since < datetime(params['end_year'] + 1, 1, 1)),
                    (EaglesMembership.expire_at == None) \
                    | (EaglesMembership.expire_at >= self.request.now)
                    )
                ) \
            .all()
        return handler.build_response(
            self.request,
            flavor='json',
            successful=True,
            value=memberships
            )
