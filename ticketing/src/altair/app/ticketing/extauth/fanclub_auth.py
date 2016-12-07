# encoding: UTF-8
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.sqlahelper import get_db_session
from urlparse import urljoin
from .models import OAuthServiceProvider

def get_fanclub_auth_setting(request, k):
    settings = request.organization.settings
    if settings is not None:
        fanclub_auth_settings = settings.get(u'rakuten_auth')
        if fanclub_auth_settings is not None:
            return fanclub_auth_settings.get(k)
    return None


def consumer_key_builder(request):
    # return get_fanclub_auth_setting(request, u'oauth_consumer_key')
    sp = request.organization.oauth_service_provider
    return sp.consumer_key


def consumer_secret_builder(request):
    # return get_fanclub_auth_setting(request, u'oauth_consumer_secret')
    sp = request.organization.oauth_service_provider
    return sp.consumer_secret


class FanclubEndpointBuilder(object):
    def __init__(self):
        pass

    def _get_service_provider(self, request):
        session = get_db_session(request, 'extauth')
        try:
            # extauthのrequest.organizationは関連をもっていない
            # 現状はorg:spは1:1の前提
            sp = session.query(OAuthServiceProvider).filter_by(organization_id=request.organization.id).one()
        except NoResultFound as e:
            raise e
        except MultipleResultsFound as e:
            raise e
        return sp

    def request_token_endpoint(self, request):
        service_provider = self._get_service_provider(request)
        return urljoin(service_provider.endpoint_base, '/fc/api/oauth1/initiate')

    def authorization_endpoint(self, request):
        service_provider = self._get_service_provider(request)
        return urljoin(service_provider.endpoint_base, '/fc/api/oauth1/authorize')

    def access_token_endpoint(self, request):
        service_provider = self._get_service_provider(request)
        return urljoin(service_provider.endpoint_base, '/fc/api/oauth1/token')

    def member_info_endpoint(self, request):
        service_provider = self._get_service_provider(request)
        return urljoin(service_provider.endpoint_base, '/fc/api/v1/member_data')
