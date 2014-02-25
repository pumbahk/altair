import logging

from pyramid.interfaces import IRequest, IView, IViewClassifier
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from pyramid.config import ConfigurationError
from .interfaces import IAuthenticationChallengeViewClassifier

logger = logging.getLogger(__name__)

def add_challenge_view(config, view=None, context=None, view_name=None):
    if view is not None:
        view = config.maybe_dotted(view)
    elif view_name is not None:
        view = config.registry.getAdapter(
            (IViewClassifier, IRequest, context),
            IView,
            view_name)
    else:
        raise ConfigurationError('either view or view_name must be specified')
    if context is not None:
        context = config.maybe_dotted(context)
    else:
        context = Interface

    logger.debug("registering challenge view: %r" % view)
    logger.debug((IAuthenticationChallengeViewClassifier, IRequest, context))
    config.registry.registerAdapter(
        view,
        (IAuthenticationChallengeViewClassifier, IRequest, context),
        IView
        )

def authentication_policy_factory(config, prefix):
    def coerce_value(k, v):
        if k == 'callback':
            v = config.maybe_dotted(v)
        return v
    authentication_policy_class = config.maybe_dotted(config.registry.settings.get(prefix))
    prefix_followed_by_a_dot = prefix + '.'
    policy_settings = {}
    for k, v in config.registry.settings.items():
        if k.startswith(prefix_followed_by_a_dot):
            _k = k[len(prefix_followed_by_a_dot):]
            v = coerce_value(_k, v)
            policy_settings[_k] = v
    return authentication_policy_class(**policy_settings)
