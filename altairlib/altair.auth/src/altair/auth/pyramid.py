# encoding: utf-8

from __future__ import absolute_import
import logging
import itertools
from zope.interface import implementer, providedBy, alsoProvides
from pyramid.httpexceptions import HTTPForbidden
from pyramid.interfaces import IAuthenticationPolicy, IRequest, IViewClassifier, IView, IMultiView
from pyramid.security import Everyone, Authenticated, principals_allowed_by_permission

from .api import get_auth_api, get_who_api, decide, get_request_classifier, get_plugin_registry
from .interfaces import ISessionKeeper, IForbiddenHandler, IAltairAuthRequest, IRequestInterceptor


logger = logging.getLogger(__name__)

authenticator_prefix = 'altair.auth.authenticator:'

@implementer(ISessionKeeper)
class PyramidSessionBasedSessionKeeperPlugin(object):
    name_base = 'pyramid_session:'

    def __init__(self, key=__name__):
        self.key = key

    @property
    def name(self):
        return self.name_base + self.key

    def get_auth_factors(self, request, auth_context, credentials=None):
        return request.session.get(self.key)

    def forget(self, request, auth_context, response, auth_factor):
        try:
            del request.session[self.key]
        except KeyError:
            pass

    def remember(self, request, auth_context, response, auth_factor):
        existing_auth_factor = request.session.setdefault(self.key, {})
        existing_auth_factor.update(auth_factor)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__,
                            id(self)) #pragma NO COVERAGE

@implementer(IAuthenticationPolicy)
class AuthenticationPolicy(object):
    def __init__(self, registry, callback=None):
        self.registry = registry
        self._callback = callback

    def __repr__(self):
        return "{0} callback={1}".format(str(type(self)), str(self._callback))

    def unauthenticated_userid(self, request):
        return self._get_identities(request)[0]

    def authenticated_userid(self, request):
        """ See IAuthenticationPolicy.
        """
        return self._get_identities(request)[0]

    def effective_principals(self, request):
        """ See IAuthenticationPolicy.
        """
        identities, _ = self._get_identities(request)
        if not identities:
            return [Everyone]
        principals = [
            authenticator_prefix + '+'.join(authenticator_names)
            for authenticator_names in (
                sorted(
                    authenticator_name
                    for authenticator_name in authenticator_names
                    if authenticator_name is not None
                    )
                for r in range(1, len(identities) + 1)
                for authenticator_names in itertools.combinations(identities.keys(), r)
                )
            ]
        logger.debug('yielded principals=%r' % principals)
        groups = self._get_groups(identities, request)
        if groups is not None:
            principals.extend(groups)
        return principals

    def remember(self, request, principal, **kw):
        api = self._getAPI(request)
        if api is None:
            return []
        _, auth_factors = self._get_identities(request)
        response = api.remember(auth_factors)
        return response.headerlist

    def forget(self, request):
        """ See IAuthenticationPolicy.
        """

        api = self._getAPI(request)
        if api is None:
            return []
        _, auth_factors = self._get_identities(request)
        response = api.forget(auth_factors)
        return response.headerlist

    def _get_groups(self, identities, request):
        if identities is not None:
            if self._callback:
                dynamic = self._callback(identities, request)
                if dynamic is not None:
                    groups = list(dynamic)
                    groups.append(Authenticated)
                    groups.append(Everyone)
                    return groups
        return [Everyone]

    def _getAPI(self, request):
        return get_who_api(request)

    def _get_identities(self, request):
        identities = request.environ.get('altair.auth.identities')
        auth_factors = request.environ.get('altair.auth.auth_factors')
        metadata = request.environ.get('altair.auth.metadata')
        if identities is None:
            api = self._getAPI(request)
            if api is None:
                return None
            identities, auth_factors, metadata = api.authenticate()
        alsoProvides(request, IAltairAuthRequest)
        request.altair_auth_metadata = metadata
        return identities, auth_factors

def get_required_permissions(context, request):
    context_iface = providedBy(context)
    view_callable = request.registry.adapters.lookup(
        (IViewClassifier, request.request_iface, context_iface),
        IView
        )
    if view_callable is not None:
        if IMultiView.providedBy(view_callable):
            permissions = (getattr(view_callable, '__permission__', None) for _, view, _ in view_callable.get_views(request))
        else:
            permissions = (getattr(view_callable, '__permission__', None), )
        permissions = set(permission for permission in permissions if permission is not None)
    else:
        permissions = set()
    return permissions

def get_required_principals(context, request, permissions):
    return set(
        itertools.chain.from_iterable(
            principals_allowed_by_permission(context, permission)
            for permission in permissions
            )
        )

def challenge_view(context, request):
    response = None
    try:
        classifier = get_request_classifier(request)
        classification = classifier(request) if classifier is not None else None
        plugin_names = decide(request, classification=classification)
        # decider が明示的に与えられていない or decider が None を返した場合は、principals から challenge すべき認証方式を調べる
        if plugin_names is None:
            logger.debug('plugin names are not provided explicitly; trying to guess from the required principals')
            permissions = get_required_permissions(request.context, request)
            principals = get_required_principals(request.context, request, permissions)
            plugin_names = set(itertools.chain.from_iterable(
                principal[len(authenticator_prefix):].split('+')
                for principal in principals
                if principal.startswith(authenticator_prefix)
                ))
            logger.debug('guessed=%r' % plugin_names)
        else:
            logger.debug('plugin names are provided explicitly; %r' % plugin_names)
            plugin_names = set(plugin_names)

        api = get_auth_api(request)
        identities, auth_factors, metadata = api.authenticate(
            request,
            decider=lambda request, plugin: ISessionKeeper.providedBy(plugin) or plugin.name in plugin_names
            )
        unauthenticated_plugin_names = plugin_names - identities.viewkeys() if identities is not None else plugin_names
        logger.debug("unauthenticated plugins=%r" % unauthenticated_plugin_names)
        logger.debug('challenge: api=%r, context=%s' % (api, context))
        if len(unauthenticated_plugin_names) > 0:
            response = HTTPForbidden()
            for plugin_name in unauthenticated_plugin_names:
                if api.challenge(request, response, challenger_name=plugin_name):
                    logger.debug('plugin requesting challenge: %s' % plugin_name)
                    break
    except Exception:
        logger.exception("OOPS!")
        raise
    if response is None:
        handler = request.registry.getUtility(IForbiddenHandler)
        if handler is not None:
            logger.debug('forbidden_handler: %r' % handler)
            try:
                response = handler(context, request)
            except Exception:
                logger.exception('OOPS!')
    if response is None:
        msg = u'authentication failed where no challenges are necessary'
        logger.error(msg)
        return HTTPForbidden(detail=u'We are experiencing a system error that you cannot get around at the moment. Sorry for the inconvenience... (guru meditation: {0})'.format(msg), content_type='text/plain')
    else:
        return response


class InterceptorTween(object):
    def __init__(self, handler, registry):
        self.handler = handler

    def __call__(self, request):
        plugin_registry = get_plugin_registry(request)
        plugins = plugin_registry.lookup_by_interface(IRequestInterceptor)
        for plugin in plugins:
            response = plugin.intercept(request)
            if response is not None:
                return response
        return self.handler(request)
