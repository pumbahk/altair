from pyramid.view import view_config
from pyramid.httpexceptions import HTTPException
from altaircms.page.api import StaticPageNotFound
from .exceptions import UsersiteException, IgnorableSystemException

__all__ = [
    'make_exc_trap_wrapper',
    'usersite_view_config',
    ]

def make_exc_trap_wrapper(view_callable):
    def exc_trap_wrapper(context, request):
        try:
            return view_callable(context, request)
        except (HTTPException, UsersiteException, StaticPageNotFound):
            raise
        except:
            raise IgnorableSystemException(u'untrapped system exception')
    return exc_trap_wrapper

def usersite_view_config(*args, **kwargs):
    decorator = kwargs.pop('decorator', None)
    if decorator is not None:
        _decorator = lambda view_callable: make_exc_trap_wrapper(decorator(view_callable))
    else:
        _decorator = make_exc_trap_wrapper
    return view_config(*args, decorator=_decorator, **kwargs)
