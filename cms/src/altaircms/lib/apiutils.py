from pyramid.threadlocal import get_current_registry
def get_registry(request):
    if request:
        return request.registry
    else:
        return get_current_registry()
