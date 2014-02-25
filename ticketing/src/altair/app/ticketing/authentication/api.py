import logging
from pyramid.compat import map_
from pyramid.interfaces import IView
from zope.interface import providedBy
from .interfaces import IAuthenticationChallengeViewClassifier

logger = logging.getLogger(__name__)

def get_authentication_challenge_view(context, request):
    provides = [IAuthenticationChallengeViewClassifier] + map_(providedBy, [request, context])
    view = request.registry.adapters.lookup(provides, IView)
    return view

