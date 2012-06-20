# -*- coding:utf-8 -*-

import urllib
import urllib2
import pickle
import urlparse
import time
import uuid
import hmac
import hashlib

from datetime import datetime
import oauth2 as oauth
from pyramid import security
from ticketing.cart import logger

from .interfaces import IRakutenOpenID
import random
from .. import helpers as cart_helpers
from ticketing.models import DBSession
from ticketing.users.models import UserProfile

def gen_reseve_no(order_no):
    base = "%012d" % order_no
    r = random.randint(0, 1000)
    base += "%03d" % r
    return base + checkdigit(base)

def checkdigit(numbers):
    numbers = list(reversed(numbers))
    evens = 0
    for n in numbers[::2]:
        evens += int(n)

    odds = 0
    for n in numbers[1::2]:
        odds += int(n)

    check = 10 - (evens * 3 + odds) % 10
    if check == 10:
        check = 0
    return str(check)
    
def get_return_url(request):
    session = request.environ['session.rakuten_openid']
    return session.get('return_url')

def authenticated_user(request):
    data = security.authenticated_userid(request)
    if data is None:
        return None
    
    return pickle.loads(data.decode('base64'))

def remember_user(request, user_data):
    data = pickle.dumps(user_data)
            
    headers = security.remember(request, data.encode('base64'))
    return headers

def get_open_id_consumer(request):
    return request.registry.queryUtility(IRakutenOpenID)

DEFAULT_BASE_URL = 'https://api.id.rakuten.co.jp/openid/auth'
DEFAULT_OAUTH_URL = 'https://api.id.rakuten.co.jp/openid/oauth/accesstoken'

class RakutenOpenID(object):
    def __init__(self, base_url, return_to, consumer_key, 
            secret=None, access_token_url=None, extra_verify_urls=None):
        self.base_url = base_url
        self.return_to = return_to
        self.consumer_key = consumer_key
        self.secret = secret
        if extra_verify_urls is None:
            self.extra_verify_urls = []
        else:
            self.extra_verify_urls = extra_verify_urls
        self.access_token_url = access_token_url



    def get_redirect_url(self):
        return (self.base_url + "?openid.ns=http://specs.openid.net/auth/2.0"
                "&openid.return_to=%(return_to)s"
                "&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select"
                "&openid.identity=http://specs.openid.net/auth/2.0/identifier_select"
                "&openid.mode=checkid_setup"
                "&openid.ns.oauth=http://specs.openid.net/extenstions/oauth/1.0"
                "&openid.oauth.consumer=%(consumer_key)s"
                "&openid.oauth.scope=rakutenid_basicinfo,rakutenid_contactinfo,rakutenid_pointaccount"
                "&openid.ns.ax=http://openid.net/srv/ax/1.0"
                "&openid.ax.mode=fetch_request"
                "&openid.ax.type.nickname=http://schema.openid.net/namePerson/friendly"
                "&openid.ax.required=nickname"
                ) % dict(return_to=self.return_to, consumer_key=self.consumer_key)

    def openid_params(self, request):
        request_get = request.GET
        return dict(ns = request_get['openid.ns'],
                    op_endpoint = request_get['openid.op_endpoint'],
                    claimed_id = request_get['openid.claimed_id'],
                    response_nonce = request_get['openid.response_nonce'],
                    mode = 'check_authentication',
                    identity = request_get['openid.identity'],
                    return_to = request_get['openid.return_to'],
                    assoc_handle = request_get['openid.assoc_handle'],
                    signed = request_get['openid.signed'],
                    sig = request_get['openid.sig'],
                    ns_oauth = 'http://specs.openid.net/extenstions/oauth/1.0',
                    oauth_request_token = request_get['openid.oauth.request_token'],
                    oauth_scope = 'rakutenid_basicinfo,rakutenid_contactinfo,rakutenid_pointaccount',
                    ns_ax = request_get['openid.ns.ax'],
                    ax_mode = request_get['openid.ax.mode'],
                    ax_type_nickname = request_get['openid.ax.type.nickname'],
                    ax_value_nickname = request_get['openid.ax.value.nickname'],
                    )

    def verify_authentication(self, request, identity):

        url = self.base_url + "?" + urllib.urlencode(
           [('openid.ns', identity['ns']),
            ('openid.op_endpoint', identity['op_endpoint']),
            ('openid.claimed_id', identity['claimed_id']),
            ('openid.response_nonce',identity['response_nonce']),
            ('openid.mode', identity['mode']),
            ('openid.identity', identity['identity']),
            ('openid.return_to', identity['return_to']),
            ('openid.assoc_handle', identity['assoc_handle']),
            ('openid.signed', identity['signed']),
            ('openid.sig', identity['sig']),
            ('openid.ns.oauth', identity['ns_oauth']),
            ('openid.oauth.request_token', identity['oauth_request_token']),
            ('openid.oauth.scope', identity['oauth_scope']),
            ('openid.ns.ax', identity['ns_ax']),
            ('openid.ax.mode', identity['ax_mode']),
            ('openid.ax.type.nickname', identity['ax_type_nickname']),
            ('openid.ax.value.nickname', identity['ax_value_nickname']),
        ])

        f = urllib2.urlopen(url)
        response_body = f.read()
        f.close()

        logger.debug('authenticate result : %s' % response_body)
        is_valid = response_body.split("\n")[0].split(":")[1]
        request_token = identity['oauth_request_token']

        access_token = self.get_access_token(self.consumer_key, request_token, self.secret)
        logger.debug('access token : %s' % access_token)

        user_info = parse_rakutenid_basicinfo(self.call_rakutenid_api(self.consumer_key, 
                                                   access_token["oauth_token"], self.secret + "&" + access_token['oauth_token_secret'],
                                                   rakuten_oauth_api='rakutenid_basicinfo',
                                                ))
        contact_info = parse_rakutenid_basicinfo(self.call_rakutenid_api(self.consumer_key, 
                                                   access_token["oauth_token"], self.secret + "&" + access_token['oauth_token_secret'],
                                                   rakuten_oauth_api='rakutenid_contactinfo',
                                                ))

        logger.debug('user_info : %s' % user_info)
        user = cart_helpers.get_or_create_user(None, identity['claimed_id'])
        if user.user_profile is None:
            profile = UserProfile(user=user)
        else:
            profile = user.user_profile

        profile.email=user_info.get('emailAddress')
        profile.nick_name=user_info.get('nickName')
        profile.first_name=user_info.get('firstName')
        profile.last_name=user_info.get('lastName')
        profile.first_name_kana=user_info.get('firstNameKataKana')
        profile.last_name_kana=user_info.get('lastNameKataKana')
        profile.birth_day=datetime.strptime(user_info.get('birthDay'), '%Y/%m/%d')
        profile.sex=self.sex_no(user_info.get('sex'))
        profile.zip=contact_info.get('zip')
        profile.prefecture=contact_info.get('prefecture')
        profile.city=contact_info.get('city')
        profile.street=contact_info.get('street')
        profile.tel_1=contact_info.get('tel')
        
        DBSession.add(user)
        import transaction
        transaction.commit()

        if is_valid == "true":
            logger.debug("authentication OK")
            return {'clamed_id': identity['claimed_id'], "nickname": identity['ax_value_nickname']}
        else:
            logger.debug("authentication NG")
            return None

    def sex_no(self, s):
        if s == u'男性':
            return 1
        elif s == u'女性':
            return 2
        else:
            return 0

    def get_access_token(self, oauth_consumer_key, oauth_token, secret):
        method = "GET"
        url = self.access_token_url
        oauth_timestamp = int(time.time() * 1000)
        oauth_nonce = uuid.uuid4().hex
        oauth_signature_method = 'HMAC-SHA1'
        oauth_version = '1.0'
        oauth_signature = create_oauth_sigunature(method, url, oauth_consumer_key, secret + "&", 
            oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, [])

        params = [
            ("oauth_consumer_key", oauth_consumer_key),
            ("oauth_token", oauth_token),
            ("oauth_signature_method", oauth_signature_method),
            ("oauth_timestamp", oauth_timestamp),
            ("oauth_nonce", oauth_nonce),
            ("oauth_version", oauth_version),
            ("oauth_signature", oauth_signature),
        ]
        
        request_url = url + '?' + urllib.urlencode(params)
        logger.debug("get access token: %s" % request_url)
        f = urllib2.urlopen(request_url)
        response_body = f.read()
        f.close()
        logger.debug('raw access token : %s' % response_body)
        access_token = parse_access_token_response(response_body)
        return access_token

    def call_rakutenid_api(self, oauth_consumer_key, access_token, secret, rakuten_oauth_api):
        method = "GET"
        url = "https://api.id.rakuten.co.jp/openid/oauth/call"
        oauth_token = access_token
        oauth_timestamp = int(time.time() * 1000)
        oauth_nonce = uuid.uuid4().hex
        oauth_signature_method = 'HMAC-SHA1'
        oauth_version = '1.0'
        oauth_signature = create_oauth_sigunature(method, url, oauth_consumer_key, secret, 
            oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, 
            [("rakuten_oauth_api", rakuten_oauth_api)])

        params = [
            ("oauth_consumer_key", oauth_consumer_key),
            ("oauth_token", oauth_token),
            ("oauth_signature_method", oauth_signature_method),
            ("oauth_timestamp", oauth_timestamp),
            ("oauth_nonce", oauth_nonce),
            ("oauth_version", oauth_version),
            ("oauth_signature", oauth_signature),
            ("rakuten_oauth_api", rakuten_oauth_api),
        ]

        request_url = url + '?' + urllib.urlencode(params)
        logger.debug("get user_info: %s" % request_url)
        try:
            f = urllib2.urlopen(request_url)
            response_body = f.read()
            f.close()
            return response_body
        except urllib2.HTTPError as e:
            logger.debug(e.read())
            logger.exception(e)
            raise

def parse_access_token_response(response):
    return dict([(key, value[0]) for key, value in urlparse.parse_qs(response).items()])
    #return dict([line.split(":", 1) for line in response.split("\n")])

def parse_rakutenid_basicinfo(response):
    
    return dict([line.split(":", 1) for line in response.split("\n")])

def create_signature_base(method, url, oauth_consumer_key, secret, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params):
    params = sorted(form_params + [
        ("oauth_consumer_key", oauth_consumer_key),
        ("oauth_token", oauth_token),
        ("oauth_signature_method", oauth_signature_method),
        ("oauth_timestamp", str(oauth_timestamp)),
        ("oauth_nonce", oauth_nonce),
        ("oauth_version", oauth_version), 
    ])

    msg = method + "&" + urllib.quote(url, safe="") + "&" + urllib.quote(urllib.urlencode(params), safe="")
    logger.debug("oauth base: %s" % msg)
    return msg

def create_oauth_sigunature(method, url, oauth_consumer_key, secret, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params):
    msg = create_signature_base(method, url, oauth_consumer_key, secret, oauth_token, oauth_signature_method, oauth_timestamp, oauth_nonce, oauth_version, form_params)
    logger.debug("secret: %s" % secret)
    oauth_signature = hmac.new(secret, msg, hashlib.sha1).digest().encode('base64')
    return oauth_signature.strip()
