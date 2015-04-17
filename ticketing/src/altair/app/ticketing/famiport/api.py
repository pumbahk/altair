# -*- coding:utf-8 -*-

from .builders import FamiPortResponseBuilderFactory, XmlFamiPortResponseGenerator


def get_response_builder(famiport_request):
    """Get appropriate FamiPortResponseBuilder for the given FamiPortRequest.

    :param famiport_request: FamiPortRequest object to get FamiPortResponseBuilder for.
    :return: Instance object of appropriate FamiPortResponseBuilder for famiport_request.
    """
    return FamiPortResponseBuilderFactory(famiport_request)

def get_xmlResponse_generator(famiport_response):
    """Get appropriate XmlFamiPortResponseGenerator for the given FamiPortResponse

    :param famiport_response: FamiPortResponse object to get XmlFamiPortResponseGenerator for.
    :return: XmlFamiPortResponseGenerator instance to generate XML of famiport_response.
    """
    return XmlFamiPortResponseGenerator(famiport_response)
