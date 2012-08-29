from .interfaces import ICompleteMail
from pyramid.interfaces import IRequest

def get_complete_mail(request):
    cls = request.registry.adapters.lookup([IRequest], ICompleteMail, "")
    return cls(request)
