import logging

import simplejson

import requests

from altair.app.ticketing.cooperation.rakuten_live.interfaces import IRakutenLiveApiCommunicator
from altair.app.ticketing.cooperation.rakuten_live.utils import generate_auth_header_value
from zope.interface import implementer

logger = logging.getLogger(__name__)


@implementer(IRakutenLiveApiCommunicator)
class RakutenLiveApiCommunicator(object):
    def __init__(self, url, api_key, api_secret, service_id, timeout):
        self.url = url
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
        headers = {
            'Content-Type': 'application/json',
            'Authorization': generate_auth_header_value(self.api_key, self.api_secret)
        }
        data['service_id'] = int(self.service_id)
        logger.debug('Sending a post to R-Live... request data: {}'.format(data))
        return requests.post(self.url, data=simplejson.dumps(data), headers=headers, timeout=float(self.timeout))


def includeme(config):
    url = config.registry.settings.get('r-live.api_url')
    api_key = config.registry.settings.get('r-live.api_key')
    api_secret = config.registry.settings.get('r-live.api_secret')
    service_id = config.registry.settings.get('r-live.service_id')
    timeout = config.registry.settings.get('r-live.timeout')
    communicator = RakutenLiveApiCommunicator(url, api_key, api_secret, service_id, timeout)
    config.registry.registerUtility(communicator, IRakutenLiveApiCommunicator)
