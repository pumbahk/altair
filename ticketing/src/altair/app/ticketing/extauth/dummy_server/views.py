from pyramid.view import view_defaults, view_config
from .models import EaglesUser
from sqlalchemy import orm

@view_defaults(renderer='json')
class EaglesExtauthAPI(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(context=orm.exc.NoResultFound)
    def no_result_found(self):
        self.request.response.status = 404
        return {
            u'status': u'error',
            u'message': u'not found'
            }

    @view_config(route_name='eagles_extauth.user_profile', request_method='POST')
    def user_profile(self):
        openid_claimed_id = self.request.json['openid_claimed_id']
        eagles_user = self.request.sa_session.query(EaglesUser) \
            .options(orm.joinedload(EaglesUser.valid_memberships)) \
            .filter(EaglesUser.openid_claimed_id == openid_claimed_id) \
            .one()
        return {
            u'status': 'success',
            u'last_name': eagles_user.last_name,
            u'first_name': eagles_user.first_name,
            u'memberships': [
                {
                    u'kind': {
                        u'id': membership.kind.id,
                        u'name': membership.kind.name,
                        },
                    u'membership_id': membership.membership_id,
                    u'valid_since': membership.valid_since,
                    u'expire_at': membership.expire_at,
                    }
                for membership in eagles_user.valid_memberships
                ]
            }
