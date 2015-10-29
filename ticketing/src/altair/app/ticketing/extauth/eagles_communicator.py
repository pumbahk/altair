import re
import urllib2
import json
import logging
import hashlib
import six
from urllib import urlencode
from urlparse import urljoin
from datetime import datetime
from zope.interface import implementer
from .interfaces import ICommunicator
from .exceptions import CommunicationError
from altair.app.ticketing.utils import parse_content_type

logger = logging.getLogger(__name__)

@implementer(ICommunicator)
class EaglesCommunicator(object):
    def __init__(self, endpoint_base, opener_factory, client_name, hash_key, style_classes={}, request_charset='utf-8'):
        self.endpoint_base = endpoint_base
        self.opener_factory = opener_factory
        self.client_name = client_name
        self.hash_key = hash_key
        self.style_classes = style_classes
        self.request_charset = request_charset

    def _do_request(self, endpoint, data):
        req = urllib2.Request(endpoint)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=%s' % self.request_charset)
        req.add_header('Connection', 'close')
        req.add_data(
            urlencode([
                (k.encode(self.request_charset), v.encode(self.request_charset))
                for k, v in data.items()
                ])
            )
        opener = self.opener_factory()
        try:
            resp = opener.open(req)
        except urllib2.HTTPError as e:
            mime_type, charset = parse_content_type(e.info()['content-type'])
            if mime_type == 'application/json':
                try:
                    data = json.load(e, encoding=charset)
                    status = data.get('status')
                    if status != u'NG':
                        raise CommunicationError('"status" field is not "NG" (or does not exist) while the response status is not 200 OK')
                    message = data.get('message', None)
                    if message is not None:
                        raise CommunicationError(message)
                except CommunicationError:
                    raise
                except:
                    logger.exception('oops')
            raise CommunicationError('HTTP error: status=%d' % e.code)

        mime_type, charset = parse_content_type(resp.info()['content-type'])
        if mime_type != 'application/json':
            raise CommunicationError("content_type is not 'application/json' (got %s)" % mime_type)
        data = json.load(resp, encoding=charset)
        try:
            status = data.pop(u'status')
        except KeyError:
            raise CommunicationError('"status" field does not exist')
        if status != u'OK':
            if status != u'NG':
                raise CommunicationError('"status" field must be either "OK" or "NG"')
            message = data.get('message', None)
            if message is None:
                raise CommunicationError('"message" field is missing while "status" is NG')
            else:
                raise CommunicationError(message)
        return data

    def parse_datetime(self, value):
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value is not None else None
        except:
            raise CommunicationError(u'invalid date/time string: %s' % value)

    def resolve_style_name(self, member_dict):
        return self.style_classes.get(six.text_type(member_dict['course_id']), u'')

    def get_user_profile(self, openid_claimed_id):
        h = hashlib.sha224()
        h.update(openid_claimed_id)
        h.update(self.client_name)
        h.update(self.hash_key)
        token = six.text_type(h.hexdigest())
        this_year = six.text_type(datetime.now().year)
        data = self._do_request(
            urljoin(self.endpoint_base, '/user/memberships'),
            {
                u'open_id': openid_claimed_id,
                u'client_name': self.client_name,
                u'token': token,
                u'start_year': this_year,
                u'end_year':  this_year,
                }
            )
        try:
            members = data['members']
        except:
            raise CommunicationError(u'"members" field is missing')
        if not all(isinstance(member, dict) for member in members):
            raise CommunicationError(u'each element in "members" must be an object')
        try:
            return dict(
                memberships=[
                    dict(
                        membership_id=member['fc_member_id'],
                        year=member['year'],
                        registered_at=self.parse_datetime(member['admission_date']),
                        related_at=self.parse_datetime(member['rakuten_relation_date']),
                        kind=dict(
                            id=member['course_id'],
                            name=member['course_name'],
                            aux=dict(
                                style_class_name=self.resolve_style_name(member)
                                )
                            )
                        )
                    for member in members
                    ]
                )
        except KeyError as e:
            raise CommunicationError(u'"%s" field is missing in member' % e.message)

def includeme(config):
    from altair.app.ticketing.urllib2ext import opener_factory_from_config

    style_classes = {}
    for k, v in config.registry.settings.items():
        g = re.match(ur'^altair\.eagles_extauth\.member_kind_style_class\.([^.]+)', k)
        if g is not None:
            style_classes[g.group(1)] = v
    logger.debug('style_classes=%r' % style_classes)
    config.registry.registerUtility(
        EaglesCommunicator(
            endpoint_base=config.registry.settings['altair.eagles_extauth.endpoint_base'],
            opener_factory=opener_factory_from_config(config, 'altair.eagles_extauth.urllib2_opener_factory'),
            client_name=config.registry.settings['altair.eagles_extauth.client_name'],
            hash_key=config.registry.settings['altair.eagles_extauth.hash_key'],
            style_classes=style_classes
            ),
        ICommunicator
        )
