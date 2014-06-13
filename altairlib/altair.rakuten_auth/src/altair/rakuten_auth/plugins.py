# -*- coding:utf-8 -*-
import pickle
import logging
import sys
from datetime import datetime
from webob.exc import HTTPFound
from zope.interface import implementer
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator, IMetadataProvider
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
from altair.auth.api import get_current_request
from altair.browserid import get_browserid
from beaker.cache import Cache, CacheManager, cache_regions
from .api import get_rakuten_oauth, get_rakuten_id_api_factory
from .interfaces import IRakutenOpenID

from . import IDENT_METADATA_KEY

logger = logging.getLogger(__name__)

cache_manager = CacheManager(cache_regions=cache_regions)

def make_plugin(cache_region=None, **kwargs):
    return RakutenOpenIDPlugin(cache_region, **kwargs)

def sex_no(s, encoding='utf-8'):
    if isinstance(s, str):
        s = s.decode(encoding)
    if s == u'男性':
        return 1
    elif s == u'女性':
        return 2
    else:
        return 0


class RemembererWrapper(object):
    def __init__(self, impl):
        self.impl = impl

    def remember(self, environ, identity):
        return self.impl.remember(environ, {
            'repoze.who.userid': pickle.dumps({
                'claimed_id': identity['claimed_id'],
                }).encode('base64'),
            })

    def forget(self, environ):
        return self.impl.forget(environ, {})

    def get_identity(self, environ):
        identity = self.impl.identify(environ)
        if identity is None:
            return None
        # identity is encoded as user id
        payload = self.impl.authenticate(environ, identity)
        retval = None
        try:
            retval = pickle.loads(payload.decode('base64'))
        except:
            pass
        return retval


@implementer(IIdentifier, IAuthenticator, IChallenger, IMetadataProvider)
class RakutenOpenIDPlugin(object):
    cache_manager = cache_manager
    AUTHENTICATED_KEY = __name__ + '.authenticated'
    METADATA_KEY = __name__ + '.metadata'

    def __init__(self, cache_region=None, **kwargs):
        if cache_region is None:
            cache_region = __name__ + '.metadata'
        self.cache_region = cache_region
        self.rememberer = RemembererWrapper(AuthTktCookiePlugin(**kwargs))

    def _get_cache(self):
        return self.cache_manager.get_cache_region(
            __name__ + '.' + self.__class__.__name__,
            self.cache_region
            )

    def _get_impl(self, environ):
        request = get_current_request(environ)
        return request.registry.queryUtility(IRakutenOpenID)

    def _get_extras(self, request, identity):
        access_token = get_rakuten_oauth(request).get_access_token(identity['oauth_request_token'])
        idapi = get_rakuten_id_api_factory(request)(access_token)
        user_info = idapi.get_basic_info()
        birthday = None
        try:
            birthday = datetime.strptime(user_info.get('birthDay'), '%Y/%m/%d')
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
            birthday=birthday,
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
        req = get_current_request(environ)
        logger.debug('identify (req.path_url=%s)' % req.path_url)
        identity = environ.get(self.AUTHENTICATED_KEY)
        if not identity:
            # backwards compatibility
            identity = self.rememberer.get_identity(req.environ)
            logging.debug('got identity from rememberer: %s' % identity)
        return identity

    # IAuthenticator
    def authenticate(self, environ, identity):
        req = get_current_request(environ)
        impl = self._get_impl(environ)
        logger.debug('authenticate (req.path_url=%s, identity=%s)' % (req.path_url, identity))

        # login() から呼ばれた場合
        openid_params = identity.get(impl.IDENT_OPENID_PARAMS_KEY, None)
        if openid_params is not None:
            if not environ.get(self.AUTHENTICATED_KEY):
                # not verified yet
                claimed_id = openid_params['claimed_id']
                self._flush_cache(claimed_id)
                if not impl.verify_authentication(req, openid_params):
                    logger.debug('authentication failed')
                    return None
                # claimed_id と oauth_request_token は、validate に成功した時のみ入る
                identity['claimed_id'] = claimed_id
                identity['oauth_request_token'] = openid_params['oauth_request_token']
                # temporary session や rememberer には OpenID parameters は渡さない
                del identity[impl.IDENT_OPENID_PARAMS_KEY]

        if 'claimed_id' not in identity:
            return None

        # extra_verify もしくは普通のリクエストで通る
        # ネガティブキャッシュなので、not in で調べる
        logger.debug('metadata=%r' % environ.get(self.METADATA_KEY, '*not set*'))
        if self.METADATA_KEY not in environ:
            cache = self._get_cache()

            def get_extras():
                retval = self._get_extras(req, identity)
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
            environ[self.METADATA_KEY] = extras
        else:
            # ネガティブキャッシュなので extras is None になる可能性
            extras = environ[self.METADATA_KEY]
        if extras is None:
            # ユーザ情報が取れない→ポイント口座番号が取れない
            # →クリティカルな状況と考えられるので認証失敗
            logger.info("Could not retrieve extra information")
            return None

        environ[self.AUTHENTICATED_KEY] = identity
        return identity['claimed_id']

    # IIdentifier
    def remember(self, environ, identity):
        req = get_current_request(environ)
        logger.debug('remember identity (req.path_url=%s): %s' % (req.path_url, identity))
        return self.rememberer.remember(environ, identity)

    # IIdentifier
    def forget(self, environ, identity):
        req = get_current_request(environ)
        logger.debug('forget identity')
        claimed_id = identity.get('claimed_id')
        if claimed_id:
            self._flush_cache(claimed_id)
        return self.rememberer.forget(environ)

    def _flush_cache(self, claimed_id):
        try:
            self._get_cache().remove_value(claimed_id)
        except:
            logger.warning("failed to flush metadata cache for %s" % claimed_id)

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        if self.METADATA_KEY in environ:
            identity[IDENT_METADATA_KEY] = environ[self.METADATA_KEY]
            del environ[self.METADATA_KEY]

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        logger.debug('challenge')
        impl = self._get_impl(environ)
        req = get_current_request(environ)
        return impl.on_challenge(req)
