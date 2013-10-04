import venusian
from beaker.cache import CacheManager, cache_regions
from pyramid.threadlocal import get_current_request
from pyramid.config.views import requestonly
import logging

from .exceptions import TooManyCartsCreated
from .api import get_cart_user_identifiers

__all__ = (
    'LimitterDecorators',
    )

logger = logging.getLogger(__name__)

cache_manager = CacheManager(cache_regions=cache_regions)

def gen_callback(limits, setting_name):
    def _(context, name, ob):
        settings = context.config.registry.settings
        default = settings.get(setting_name, '0')
        for k in limits.keys():
            limits[k] = int(settings.get(setting_name + '.' + k, default))
    return _

class LimitterDecorators(object):
    venusian = venusian
    cache_manager = cache_manager

    def __init__(self, setting_name, exc_class, cache_region=(__name__ + '.limitter')):
        self.setting_name = setting_name
        self.exc_class = exc_class
        cache = None
        try:
            cache = self.cache_manager.get_cache_region(__name__, cache_region)
        except:
            pass
        self.cache = cache

    def acquire(self, func):
        if self.cache is None:
            return func
        limits = {'strong': 0, 'decent': 0, 'weak': 0}
        def _(*args, **kwargs):
            try:
                request = get_current_request()
                for id_, strength in get_cart_user_identifiers(request):
                    logger.debug('user_identifier=%s, strength=%s' % (id_, strength))
                    count = self.cache.get(id_, createfunc=lambda: 0) + 1
                    self.cache.put(id_, count)
                    if count > limits[strength]:
                        raise self.exc_class(id_)
            except self.exc_class:
                raise
            except Exception as e:
                import sys
                logger.error('failed to acquire counter', exc_info=sys.exc_info())

            return func_(*args, **kwargs)

        info = self.venusian.attach(
            func,
            gen_callback(limits, self.setting_name),
            category='pyramid')
        if info.scope != 'class' and requestonly(func):
            func_ = lambda _, request: func(request)
        else:
            func_ = func

        return _

    def _release(self, request):
        if self.cache is None:
            return
        for id_, _ in get_cart_user_identifiers(request):
            count = self.cache.get(id_, createfunc=lambda: 0)
            self.cache.put(id_, max(count - 1, 0))

    def release(self, func):
        if self.cache is None:
            return func
        limits = {'strong': 0, 'decent': 0, 'weak': 0}
        def _(*args, **kwargs):
            try:
                self._release(get_current_request())
            except Exception as e:
                import sys
                logger.error('failed to release counter', exc_info=sys.exc_info())
            return func_(*args, **kwargs)

        info = self.venusian.attach(
            func,
            gen_callback(limits, self.setting_name),
            category='pyramid')
        if info.scope != 'class' and requestonly(func):
            func_ = lambda _, request: func(request)
        else:
            func_ = func
        return _
