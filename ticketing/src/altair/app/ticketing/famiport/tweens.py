from altair.sqla import DBSessionContext
from sqlahelper import get_engine

def famiport_dbsession_tween_factory(handler, registry):
    def tween(request):
        from .models import _session
        _session.configure(bind=get_engine())
        with DBSessionContext(_session, name='famiport'):
            return handler(request)
    return tween
