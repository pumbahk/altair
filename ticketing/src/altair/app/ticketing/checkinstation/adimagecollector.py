# -*- coding:utf-8 -*-
from zope.interface import implementer
from .interfaces import IAdImageCollector

@implementer(IAdImageCollector)
class AdImageCollector(object):
    def __init__(self, registry):
        self.registry = registry
        self.urls = []
        self.specs = []

    def add_url(self, url):
        self.urls.append(url)

    def add_spec(self, spec):
        self.specs.append(spec)

    def get_images(self, request):
        r = []
        r.extend(self.urls)
        r.extend(request.static_url(s) for s in self.specs)
        return r


def add_ad_image(config, url=None, imagespec=None):
    collector = config.registry.queryUtility(IAdImageCollector)
    if collector is None:
        collector = AdImageCollector(config.registry)
        config.registry.registerUtility(collector, IAdImageCollector)
    if url:
        collector.add_url(url)
    if imagespec:
        collector.add_spec(imagespec)

def includeme(config):
    config.add_directive("add_ad_image", add_ad_image)
