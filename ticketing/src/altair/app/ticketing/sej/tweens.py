from altair.sqla import DBSessionContext
from sqlahelper import get_engine

def encoding_converter_tween_factory(handler, registry):
    def encoding_converter_tween(request):
        registry = getattr(request, 'registry', None)
        context = getattr(request, 'context', None)
        request = request.decode('CP932')
        if registry is not None:
            request.registry = registry
        if context is not None:
            request.context = context
        return handler(request)
    return encoding_converter_tween

def sej_dbsession_tween_factory(handler, registry):
    def tween(request):
        from .models import _session
        _session.configure(bind=get_engine())
        with DBSessionContext(_session, name='sej'):
            return handler(request)
    return tween
