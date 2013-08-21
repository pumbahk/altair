# -*- coding:utf-8 -*-
import pickle
import logging
import sys
from datetime import datetime
from webob.exc import HTTPFound
from zope.interface import implementer
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator, IMetadataProvider
from altair.auth.api import get_current_request
from altair.browserid import get_browserid
from beaker.cache import Cache, CacheManager, cache_regions
from .api import get_rakuten_oauth, get_rakuten_id_api_factory
from .interfaces import IRakutenOpenID

import traceback

logger = logging.getLogger(__name__)

cache_manager = CacheManager(cache_regions=cache_regions)

def make_plugin(rememberer_name, cache_region=None):
    return RakutenOpenIDPlugin(rememberer_name, cache_region)

def sex_no(s, encoding='utf-8'):
    if isinstance(s, str):
        s = s.decode(encoding)
    if s == u'男性':
        return 1
    elif s == u'女性':
        return 2
    else:
        return 0

@implementer(IIdentifier, IAuthenticator, IChallenger, IMetadataProvider)
class RakutenOpenIDPlugin(object):
    cache_manager = cache_manager
    AUTHENTICATED_KEY = __name__ + '.authenticated'
    METADATA_KEY = __name__ + '.metadata'

    def __init__(self, rememberer_name, cache_region=None):
        self.rememberer_name = rememberer_name
        if cache_region is None:
            cache_region = __name__ + '.metadata'
        self.cache_region = cache_region

    def _get_cache(self):
        return self.cache_manager.get_cache_region(
            __name__ + '.' + self.__class__.__name__,
            self.cache_region
            )

    def _get_impl(self, environ):
        request = get_current_request(environ)
        return request.registry.queryUtility(IRakutenOpenID)

    def _get_rememberer(self, environ):
        
        #rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        api = get_who_api(environ)
        rememberer = api.name_registry[self.rememberer_name]
        return rememberer

    def get_identity(self, req):
        rememberer = self._get_rememberer(req.environ)
        return rememberer.identify(req.environ)

    def _get_extras(self, request, identity):
        access_token = get_rakuten_oauth(request).get_access_token(identity['oauth_request_token'])
        logger.debug('access token : %s' % access_token)

        idapi = get_rakuten_id_api_factory(request)(access_token)
        user_info = idapi.get_basic_info()
        birth_day = None
        try:
            datetime.strptime(user_info.get('birthDay'), '%Y/%m/%d')
        except (ValueError, TypeError):
            # 生年月日未登録
            pass

        contact_info = idapi.get_contact_info()
        point_account = idapi.get_point_account()

        return dict(
            email_1=user_info.get('emailAddress'),
            nick_name=user_info.get('nickName'),
            first_name=user_info.get('firstName'),
            last_name=user_info.get('lastName'),
            first_name_kana=user_info.get('firstNameKataKana'),
            last_name_kana=user_info.get('lastNameKataKana'),
            birth_day=birth_day,
            sex=sex_no(user_info.get('sex'), 'utf-8'),
            zip=contact_info.get('zip'),
            prefecture=contact_info.get('prefecture'),
            city=contact_info.get('city'),
            street=contact_info.get('street'),
            tel_1=contact_info.get('tel'),
            rakuten_point_account=point_account.get('pointAccount')
            )

    # IIdentifier
    def identify(self, environ):
        impl = self._get_impl(environ)
        # return_to URLの場合にverifyする
        # それ以外の場合デシリアライズしてclaimed_idを返す
        req = get_current_request(environ)
        logger.debug('identity (req.path_url=%s, impl.verify_url=%s, impl.extra_verify_url=%s)' % (req.path_url, impl.verify_url, impl.extra_verify_url))

        identity = None

        if req.path_url == impl.verify_url:
            logging.debug('path_url is identical to verify_url. returning the passed parameters as identity for authenticate()')
            identity = impl.openid_params(req)
        else:
            # check out the temporary session first
            if req.path_url == impl.extra_verify_url:
                session = impl.get_session(req)
                if session:
                    remembered_identity = session.get(self.__class__.__name__ + '.identity')
                    if remembered_identity is not None:
                        logging.debug('got identity from temporary session: %s' % remembered_identity)
                        identity = {
                            'claimed_id': remembered_identity['claimed_id'],
                            'oauth_request_token': remembered_identity['oauth_request_token'],
                            }

            if identity is None:
                remembered_identity = self.get_identity(req)
                logging.debug('got identity from rememberer: %s' % remembered_identity)
                authenticated = remembered_identity and remembered_identity.get('repoze.who.plugins.auth_tkt.userid')
                if authenticated:
                    try:
                        identity = pickle.loads(authenticated.decode('base64'))
                    except Exception as e:
                        logger.exception(e)

        return identity

    # IAuthenticator
    def authenticate(self, environ, identity):
        userdata = None
        req = get_current_request(environ)
        impl = self._get_impl(environ)
        logger.debug('authenticate (req.path_url=%s, impl.verify_url=%s, identity=%s)' % (req.path_url, impl.verify_url, identity))
        if req.path_url == impl.verify_url and \
            self.AUTHENTICATED_KEY not in environ:
            self._flush_cache(identity)
            if not impl.verify_authentication(req, identity):
                logger.debug('authentication failed')
                return None
            # We don't want to keep everything in it.
            userdata = {
                'claimed_id': identity['claimed_id'],
                'oauth_request_token': identity['oauth_request_token'],
                }
        else:
            if 'claimed_id' in identity:
                userdata = identity

                cache = self._get_cache()

                def get_extras():
                    retval = self._get_extras(req, identity)
                    session = impl.get_session(req)
                    browserid = get_browserid(req)
                    retval['browserid'] = browserid
                    return retval

                extras = None
                try:
                    extras = cache.get(
                        key=identity['claimed_id'],
                        createfunc=get_extras
                        )
                except:
                    logger.warning("Failed to retrieve extra information", exc_info=sys.exc_info())
                if not extras:
                    # ユーザ情報が取れない→ポイント口座番号が取れない
                    # →クリティカルな状況と考えられるので認証失敗
                    logger.info("Could not retrieve extra information")
                    return None
                environ[self.METADATA_KEY] = extras

        if userdata:
            environ[self.AUTHENTICATED_KEY] = True
            return (pickle.dumps(userdata)).encode('base64')
        else:
            return None

    # IIdentifier
    def remember(self, environ, identity):
        req = get_current_request(environ)
        impl = self._get_impl(environ)
        logger.debug('remember identity (req.path_url=%s, impl.verify_url=%s): %s' % (req.path_url, impl.verify_url, identity))
        if req.path_url == impl.verify_url:
            session = impl.get_session(req)
            if session is not None:
                session[self.__class__.__name__ + '.identity'] = identity
                session.save()
            else:
                logger.warning('could not retrieve session')
        rememberer = self._get_rememberer(environ)
        return rememberer.remember(environ, identity)

    # IIdentifier
    def forget(self, environ, identity):
        req = get_current_request(environ)
        impl = self._get_impl(environ)
        logger.debug('forget identity')
        self._flush_cache(identity)
        session = impl.get_session(req)
        session and session.clear()
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)

    def _flush_cache(self, identity):
        try:
            self._get_cache().remove_value(identity['claimed_id'])
        except:
            logger.warning("failed to flush metadata cache for %s" % identity)

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        if self.METADATA_KEY in environ:
            identity.update(environ[self.METADATA_KEY])
            del environ[self.METADATA_KEY]

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        logger.debug('challenge')
        request = get_current_request(environ)
        impl = self._get_impl(environ)
        session = impl.new_session(request)
        impl.set_return_url(session, request.url)
        session.save()
        logger.debug('redirect from %s' % request.url)
        return HTTPFound(location=impl.get_redirect_url(session))
