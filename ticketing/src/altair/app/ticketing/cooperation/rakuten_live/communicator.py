import logging

from standardenum import StandardEnum

import simplejson

import requests

from altair.app.ticketing.cooperation.rakuten_live.interfaces import IRakutenLiveApiCommunicator
from altair.app.ticketing.cooperation.rakuten_live.utils import generate_r_live_auth_hash
from zope.interface import implementer

logger = logging.getLogger(__name__)


class RakutenLiveApiCode(StandardEnum):
    SUCCESS = 1
    INTERNAL_SERVER_ERROR = 500
    ACCESS_TOKEN_INVALID = 1062


@implementer(IRakutenLiveApiCommunicator)
class RakutenLiveApiCommunicator(object):
    def __init__(self, url, auth_type, api_key, api_secret, service_id, timeout):
        self.url = url
        self.auth_type = auth_type
        self.api_key = api_key
        self.api_secret = api_secret
        self.service_id = service_id
        self.timeout = timeout

    def post(self, data):
        """
        Send a post to R-Live with the given data
        :param data: dictionary data to become the request json
        :return: requests.models#Response
        """
        authorization = '{} {}'.format(self.auth_type, generate_r_live_auth_hash(self.api_key, self.api_secret))
        headers = {
            'Content-Type': 'application/json',
            'Authorization': authorization
        }
        data['service_id'] = int(self.service_id)
        logger.debug('Sending a post to R-Live... request data: {}'.format(data))
        return requests.post(self.url, data=simplejson.dumps(data), headers=headers, timeout=float(self.timeout))


def includeme(config):
    url = config.registry.settings.get('r-live.api_url')
    auth_type = config.registry.settings.get('r-live.auth_type')
    api_key = config.registry.settings.get('r-live.api_key')
    api_secret = config.registry.settings.get('r-live.api_secret')
    service_id = config.registry.settings.get('r-live.service_id')
    timeout = config.registry.settings.get('r-live.timeout')
    communicator = RakutenLiveApiCommunicator(url, auth_type, api_key, api_secret, service_id, timeout)
    config.registry.registerUtility(communicator, IRakutenLiveApiCommunicator)
