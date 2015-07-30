# -*- coding: utf-8 -*-
from lxml import etree


def famiport_renderer_factory(info):
    def _render(value, system):
        request = system.get('request')
        charset = 'cp932'
        if request is not None:
            response = request.response
            ct = response.content_type
            response.charset = charset
            if ct == response.default_content_type:
                response.content_type = 'text/xml'
        return etree.tostring(value, xml_declaration=True, encoding=charset)
    return _render


def famiport_text_renderer_factory(info):
    def _render(value, system):
        request = system.get('request')
        charset = 'cp932'
        if request is not None:
            response = request.response
            response.charset = charset
            response.content_type = 'text/plain charset=shift_jis'
        return value
    return _render
