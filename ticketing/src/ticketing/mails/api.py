from .interfaces import ICompleteMail
from pyramid.interfaces import IRequest
import logging

logger = logging.getLogger(__name__)

def get_complete_mail(request):
    cls = request.registry.adapters.lookup([IRequest], ICompleteMail, "")
    return cls(request)

