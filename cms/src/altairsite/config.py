from pyramid.view import view_config
from pyramid.httpexceptions import HTTPException
from altaircms.page.api import StaticPageNotFound
from altairsite.separation import enable_mobile, enable_smartphone
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

def pop_decorator(kwargs):
    decorator = kwargs.pop('decorator', None)
    if decorator is not None:
        return lambda view_callable: make_exc_trap_wrapper(decorator(view_callable))
    else:
        return make_exc_trap_wrapper

def pop_custom_predicates(kwargs, predicate):
    _custom_predicates = kwargs.pop("custom_predicates", [])
    _custom_predicates = list(_custom_predicates)
    _custom_predicates.insert(0, enable_mobile)
    return _custom_predicates
    
def usersite_view_config(*args, **kwargs):
    _decorator = pop_decorator(kwargs)
    return view_config(*args, decorator=_decorator, **kwargs)

def usersite_add_view(config, *args, **kwargs):
    _decorator = pop_decorator(kwargs)
    config.add_view(*args,  decorator=_decorator, **kwargs)

def mobile_site_view_config(*args, **kwargs):
    _decorator = pop_decorator(kwargs)
    _custom_predicates = pop_custom_predicates(kwargs, enable_mobile)
    return view_config(*args, decorator=_decorator, custom_predicates=_custom_predicates, **kwargs)

def mobile_site_add_view(config, *args, **kwargs):
    _decorator = pop_decorator(kwargs)
    _custom_predicates = pop_custom_predicates(kwargs, enable_mobile)
    config.add_view(*args,  decorator=_decorator, custom_predicates=_custom_predicates, **kwargs)

def smartphone_site_view_config(*args, **kwargs):
    _decorator = pop_decorator(kwargs)
    _custom_predicates = pop_custom_predicates(kwargs, enable_smartphone)
    return view_config(*args, decorator=_decorator, custom_predicates=_custom_predicates, **kwargs)

def smartphone_site_add_view(config, *args, **kwargs):
    _decorator = pop_decorator(kwargs)
    _custom_predicates = pop_custom_predicates(kwargs, enable_smartphone)
    config.add_view(*args,  decorator=_decorator, custom_predicates=_custom_predicates, **kwargs)

def install_convinient_request_properties(config):
    assert config.registry.settings["altair.orderreview.url"]
    def altair_orderreview_url(request):
        return config.registry.settings["altair.orderreview.url"]

    assert config.registry.settings["getti.orderreview.url"]
    def getti_orderreview_url(request):
        return config.registry.settings["getti.orderreview.url"]

    assert config.registry.settings["lots.orderreview.url"]
    def lots_orderreview_url(request):
        return config.registry.settings["lots.orderreview.url"]

    assert config.registry.settings["sender.mailaddress"]
    def sender_mailaddress(request):
        return config.registry.settings["sender.mailaddress"]

    assert config.registry.settings["inquiry.mailaddress"]
    def inquiry_mailaddress(request):
        if request.organization.short_name == "RT":
            return config.registry.settings["inquiry.rt.mailaddress"]
        if request.organization.short_name == "ST":
            return config.registry.settings["inquiry.st.mailaddress"]

    config.set_request_property(altair_orderreview_url, "altair_orderreview_url", reify=True)
    config.set_request_property(getti_orderreview_url, "getti_orderreview_url", reify=True)
    config.set_request_property(lots_orderreview_url, "lots_orderreview_url", reify=True)
    config.set_request_property(sender_mailaddress, "sender_mailaddress", reify=True)
    config.set_request_property(inquiry_mailaddress, "inquiry_mailaddress", reify=True)
    config.set_request_property("altairsite.mobile.dispatch.views.mobile_route_path", "mobile_route_path", reify=True)

def includeme(config):
    config.add_directive("usersite_add_view", usersite_add_view)
    config.add_directive("mobile_site_add_view", mobile_site_add_view)
    config.add_directive("smartphone_site_add_view", smartphone_site_add_view)
