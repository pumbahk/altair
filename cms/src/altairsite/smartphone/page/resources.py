# -*- coding:utf-8 -*-
from ..common.resources import CommonResource
from altairsite.inquiry.views import send_mail
from altairsite.mobile.core.helper import log_error

class OrderreviewUrl(object):
    def __init__(self, getti, altair):
        self.getti = getti
        self.altair = altair

class PageResource(CommonResource):

    def get_orderreview_url(self):
        altair = self.request.altair_orderreview_url
        getti = self.request.getti_orderreview_url
        return OrderreviewUrl(getti=getti, altair=altair)

    def send_inquiry_mail(self, title, create_body, form, recipients):
        ret = True
        try:
            send_mail(request=self.request, title=title, body=create_body(form), recipients=recipients)
        except Exception as e:
            ret = False
            log_error("send_inquiry_mail", str(e))
        return ret
