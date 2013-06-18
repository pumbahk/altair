# -*- coding:utf-8 -*-
from ..common.resources import CommonResource

class OrderreviewUrl(object):
    def __init__(self, getti, altair):
        self.getti = getti
        self.altair = altair

class PageResource(CommonResource):

    def get_orderreview_url(self):
        altair = self.request.altair_orderreview_url
        getti = self.request.getti_orderreview_url
        return OrderreviewUrl(getti=getti, altair=altair)
