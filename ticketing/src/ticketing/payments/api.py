from .interfaces import IGetCart

def get_cart(request):
    getter = request.registry.getUtility(IGetCart)
    return getter(request)
