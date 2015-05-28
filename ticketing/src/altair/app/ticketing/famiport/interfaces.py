# -*- coding: utf-8 -*-

from zope.interface import Interface

class IFamiPortResponseBuilderFactory(Interface):
    def __call__(self, famiport_request):
        pass

class IFamiPortResponseBuilder(Interface):
    # Build FamiPortResponse from FamiPortRequest
    def build_response(famiport_request=None):
        pass

""" Commenting out since seems not necessary at this point.
class IXmlFamiPortResponseGeneratorFactory(Interface):
    def __call__(self, famiport_response):
        pass
"""

class IXmlFamiPortResponseGenerator(Interface):
    # Generate XML text from famiport_response with encrypt_fields encrypted
    def generate_xmlResponse(famiport_response=None, encrypt_fields = []):
        pass
