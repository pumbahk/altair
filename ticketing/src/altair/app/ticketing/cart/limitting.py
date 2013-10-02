import venusian
from beaker.cache import CacheManager, cache_regions

from .exceptions import TooManyCartsCreated

__all__ = (
    'limitter',
    )

cache_manager = CacheManager(cache_regions=cache_regions)

class LimitterDecorator(object):
    venusian = venusian
    cache = cache_manager.get_cache_region(__name__)

    def __init__(self, setting_name, exc_class, cache=None):
        self.setting_name = setting_name
        self.exc_class = exc_class
        if cache is not None:
            self.cache = cache

    def __call__(self, func):
        limit = [0]
        def _(*args, **kwargs):
            request = get_current_request()
            id_ = api.get_cart_user_identifier(request)
            if id_:
                count = cache.get(id_, createfunc=lambda: 0)
                cache.put(id_, count + 1)
                if count > limit[0]:
                   raise self.exc_class(id_)

            return func(*args, **kwargs)

        def callback(context, name, ob):
            config = context.config.with_package(info.mobile)
            limit[0] = int(config.registry.settings.get(self.setting_name, '0'))

        info = self.venusian.attach(func, callback, category='pyramid')

        return _

limitter = LimitterDecorator
