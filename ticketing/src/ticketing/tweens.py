# -*- coding:utf-8 -*-
import sqlahelper
def session_cleaner_factory(handler, registry):
    def tween(request):
        sqlahelper.get_session().remove()
        try:
            return handler(request)
        finally:
            sqlahelper.get_session().remove()
    return tween
