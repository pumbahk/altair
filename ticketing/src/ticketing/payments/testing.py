# -*- coding:utf-8 -*-
from zope.interface import implementer
from .interfaces import IPaymentPreparer

@implementer(IPaymentPreparer)
class DummyPreparer(object):
    def __init__(self, result):
        self.result = result

    def prepare(self, request, cart):
        """ 決済処理の前処理を行う
        """
        return self.result
