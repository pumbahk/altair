# -*- coding:utf-8 -*-
import pickle
import logging
from .api import RakutenOpenID
import webob
from webob.exc import HTTPFound
from zope.interface import implementer
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator

logger = logging.getLogger(__name__)


def make_plugin(endpoint, return_to, consumer_key, rememberer_name):
    return RakutenOpenIDPlugin(endpoint, return_to, consumer_key, rememberer_name)

@implementer(IIdentifier, IAuthenticator, IChallenger)
class RakutenOpenIDPlugin(object):

    def __init__(self, endpoint, return_to, consumer_key, rememberer_name):
        self.endpoint = endpoint
        self.return_to = return_to
        self.consumer_key = consumer_key
        self.rememberer_name = rememberer_name
        self.impl = RakutenOpenID(endpoint, return_to, consumer_key)


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

        identity = self.get_identity(req)
        logging.debug(identity)

        if identity is None:
            return None

        if 'repoze.who.plugins.auth_tkt.userid' in identity:
            try:
                userdata = pickle.loads(identity['repoze.who.plugins.auth_tkt.userid'].decode('base64'))
                return userdata
            except Exception, e:
                logger.exception(e)


        


    # IAuthenticator
    def authenticate(self, environ, identity):
        logging.debug(identity)
        if 'clamed_id' in identity:
            return (pickle.dumps(identity)).encode('base64')


        if 'ns' not in identity:
            return

        req = webob.Request(environ)
        userdata = self.impl.verify_authentication(req, identity)
        if userdata == None:
            return None
        
        
        return (pickle.dumps(userdata)).encode('base64')



    # IIdentifier
    def remember(self, environ, identity):
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
        return HTTPFound(location=self.impl.get_redirect_url())
