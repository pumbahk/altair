# -*- coding:utf-8 -*-
import pickle
import logging
import wsgiref.util
from .api import RakutenOpenID
import webob
from webob.exc import HTTPFound
from zope.interface import implementer
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator

from ticketing.cart import logger

def make_plugin(endpoint, return_to, consumer_key, rememberer_name, oauth_secret, oauth_endpoint, extra_verify_urls=None):
    if extra_verify_urls is not None:
        extra_verify_urls = [e.strip() for e in extra_verify_urls.split()]
        logger.warn('enabled extra_verify_urls for develop mode: %s' % extra_verify_urls)
    return RakutenOpenIDPlugin(endpoint, return_to, consumer_key, rememberer_name,
        extra_verify_urls=extra_verify_urls,
        secret=oauth_secret,
        access_token_url=oauth_endpoint)

@implementer(IIdentifier, IAuthenticator, IChallenger)
class RakutenOpenIDPlugin(object):

    def __init__(self, endpoint, return_to, consumer_key, rememberer_name, extra_verify_urls, access_token_url, secret):
        self.endpoint = endpoint
        self.return_to = return_to
        self.consumer_key = consumer_key
        self.rememberer_name = rememberer_name
        self.impl = RakutenOpenID(endpoint, return_to, consumer_key, extra_verify_urls=extra_verify_urls, secret=secret)
        self.access_token_url = access_token_url

    def _get_rememberer(self, environ):

        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    def get_identity(self, req):
        rememberer = self._get_rememberer(req.environ)
        return rememberer.identify(req.environ)


    # IIdentifier
    def identify(self, environ):
        # return_to URLの場合にverifyする
        # それ以外の場合デシリアライズしてclamed_idを返す
        req = webob.Request(environ)
        if req.path_url == self.return_to:
            return self.impl.openid_params(req)

        if req.path_url in self.impl.extra_verify_urls:
            logger.warn('verify  openid for develop mode: %s' % self.impl.extra_verify_urls)
            return self.impl.openid_params(req)

        identity = self.get_identity(req)
        logging.debug(identity)

        if identity is None:
            logger.debug("identity failed")
            return None

        if 'repoze.who.plugins.auth_tkt.userid' in identity:
            try:
                userdata = pickle.loads(identity['repoze.who.plugins.auth_tkt.userid'].decode('base64'))
                return userdata
            except Exception, e:
                logger.exception(e)


        


    # IAuthenticator
    def authenticate(self, environ, identity):
        logging.debug('authenticate %s' % identity)
        if 'clamed_id' in identity:
            return (pickle.dumps(identity)).encode('base64')


        if 'ns' not in identity:
            return

        req = webob.Request(environ)
        userdata = self.impl.verify_authentication(req, identity)
        if userdata == None:
            logger.debug('authentication failed')
            return None
        
        
        return (pickle.dumps(userdata)).encode('base64')



    # IIdentifier
    def remember(self, environ, identity):
        logger.debug('remember identity')
        rememberer = self._get_rememberer(environ)
        return rememberer.remember(environ, identity)

    # IIdentifier
    def forget(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)


    # IMetadataProvider
    def add_metadata(self, environ, identity):
        # identityをデシリアライズして、nicknameを取得する
        print 'metadata'
        print identity
        identity = self.get_identity(req)
        userdata = pickle.loads(identity.decode('base64'))
        identity.update(nickname=userdata['clamed_id'])


    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        session = environ['session.rakuten_openid']
        session['return_url'] = wsgiref.util.request_uri(environ)
        logger.debug('redirect from %s' % session['return_url'])
        session.save()
        return HTTPFound(location=self.impl.get_redirect_url())
