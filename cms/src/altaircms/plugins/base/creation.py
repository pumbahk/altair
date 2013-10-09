# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from pyramid.httpexception import HTTPNotFound

class WidgetValidator(object):
    def __init__(self, request, FailureException=HTTPNotFound):
        self.request = request

    def validate(self, form):
        if not form.validate():
            logger.warn(repr(form.errors))
            raise HTTPNotFound()
        return form.data


class WidgetCreator(object):
    def __init__(self, request, FailureException=HTTPNotFound):
        self.request = request

    def validate(self, form):
        if not form.validate():
            logger.warn(repr(form.errors))
            raise HTTPNotFound()
        return form.data




