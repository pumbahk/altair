# -*- coding:utf-8 -*-

from pyramid.view import view_config

from sqlalchemy.orm import joinedload

from altaircms.event.word import api_word_get as cms_api_word_get


@view_config(route_name="api.word.get", request_method="GET", renderer='json')
def api_word_get(self, request):
    return cms_api_word_get(request)
