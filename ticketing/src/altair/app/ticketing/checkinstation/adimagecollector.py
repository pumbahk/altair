# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import json
from zope.interface import implementer
from .interfaces import IAdImageCollector
from collections import defaultdict

@implementer(IAdImageCollector)
class AdImageCollector(object):
    def __init__(self, registry):
        self.registry = registry
        self.urls = defaultdict(list)
        self.specs =defaultdict(list)

    def add_url(self, org_short_name, url):
        self.urls[org_short_name].append(url)

    def add_spec(self, org_short_name, spec):
        self.specs[org_short_name].append(spec)

    def get_images(self, request):
        r = []
        short_name = request.context.organization.short_name
        r.extend(self.urls.get(short_name) or self.urls.get("default"))
        r.extend(request.static_url(s) for s in (self.specs.get(short_name) or self.specs.get("default")))
        logger.info("ad images: %s", json.dumps(r))
        return r


def add_ad_image(config, short_name, url=None, imagespec=None):
    collector = config.registry.queryUtility(IAdImageCollector)
    if collector is None:
        collector = AdImageCollector(config.registry)
        config.registry.registerUtility(collector, IAdImageCollector)
    if url:
        collector.add_url(short_name, url)
    if imagespec:
        collector.add_spec(short_name, imagespec)

def includeme(config):
    config.add_directive("add_ad_image", add_ad_image)
