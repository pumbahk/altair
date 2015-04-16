# -*- coding:utf-8 -*-

from .builders import FamiPortResponseBuilderFactory, XmlFamiPortResponseGenerator


# Get appropriate FamiPortResponseBuilder for the given FamiPortRequest
def get_response_builder(famiport_request):
    return FamiPortResponseBuilderFactory(famiport_request)

# Get appropriate XmlFamiPortResponseGenerator for the given FamiPortResponse
def get_xmlResponse_generator(famiport_response):
    return XmlFamiPortResponseGenerator(famiport_response)
