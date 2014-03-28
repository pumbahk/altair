# -*- coding:utf-8 -*-
from zope.interface import Interface

class IAPIEndpointCollector(Interface):
    def add(name):
        pass

    def get_endpoints(request):
        """return endpoint url dict"""
        pass

class IAdImageCollector(Interface):
    def add(url):
        pass

    def get_images(request):
        """return image url list"""
        pass

