# -*- coding:utf-8 -*-
from ..common.resources import CommonResource
from altaircms.topic.models import Topic

class OrderreviewUrl(object):
    def __init__(self, getti, altair, lots):
        self.getti = getti
        self.altair = altair
        self.lots = lots

class PageResource(CommonResource):

    def get_orderreview_url(self):
        altair = self.request.altair_orderreview_url
        getti = self.request.getti_orderreview_url
        lots = self.request.lots_orderreview_url
        return OrderreviewUrl(getti=getti, altair=altair, lots=lots)

    def get_canceled_topic(self, topicid):
        if topicid:
            return self.getInfo(kind="canceled", system_tag_id=None).filter(Topic.id==topicid).first()

