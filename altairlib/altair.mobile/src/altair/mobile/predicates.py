import logging
from zope.interface import implementer

from .interfaces import ISmartphoneSupportPredicate
from . import PC_ACCESS_COOKIE_NAME

logger = logging.getLogger(__name__)

@implementer(ISmartphoneSupportPredicate)
class DefaultSmartphoneSupportPredicate(object):
    def __init__(self, enabled):
        self.enabled = enabled

    def __call__(self, request):
        return self.enabled and not PC_ACCESS_COOKIE_NAME in request.cookies

