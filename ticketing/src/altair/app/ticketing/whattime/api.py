from .interfaces import IAccessKeyGetter

def get_cms_accesskey_getter(request):
    return request.registry.queryUtility(IAccessKeyGetter, name="cms")

def get_cms_accesskey(request, accesskey):
    getter = get_cms_accesskey_getter(request)
    return getter and getter(request, accesskey)
