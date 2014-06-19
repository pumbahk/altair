from altair.sqla import DBSessionContext

def anshin_checkout_dbsession_tween_factory(handler, registry):
    def tween(request):
        from .models import _session
        with DBSessionContext(_session, name="anshin_checkout"):
            return handler(request)
    return tween

