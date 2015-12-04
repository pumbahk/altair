# -*- coding: utf-8 -*-
from lxml import etree

class XML(object):
    def __init__(self, default_charset='UTF-8', content_type='text/xml'):
        self.default_charset = default_charset
        self.content_type = content_type

    def __call__(self, info):
        def _render(value, system):
            request = system.get('request')
            charset = self.default_charset
            if request is not None:
                response = request.response
                ct = response.content_type
                if response.charset:
                    charset = response.charset
                if ct == response.default_content_type:
                    response.content_type = self.content_type
                    response.charset = charset
            return etree.tostring(value, xml_declaration=True, encoding=charset)
        return _render 
