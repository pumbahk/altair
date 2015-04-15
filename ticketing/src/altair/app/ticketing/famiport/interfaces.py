# -*- coding: utf-8 -*-

from zope.interface import Interface

class IFamiPortResponseBuilderFactory(Interface):
    def __call__(self, famiport_request):
        pass

class IFamiPortResponseBuilder(Interface):
    def build_response(famiport_request=None):
        pass