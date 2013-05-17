# -*- coding:utf-8 -*-
from ..common.helper import SmartPhoneHelper
from altairsite.config import usersite_view_config

from pyramid.view import view_defaults

@view_defaults(route_name="page",request_type="altairsite.tweens.ISmartphoneRequest")
class StaticKindView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @usersite_view_config(match_param="kind=orderreview", renderer='altairsite.smartphone:templates/page/orderreview.html')
    def move_orderreview(self):
        orderreview_url = self.context.get_orderreview_url()
        return {
            'orderreview_url':orderreview_url
        }

    @usersite_view_config(match_param="kind=canceled", renderer='altairsite.smartphone:templates/page/canceled.html')
    @usersite_view_config(match_param="kind=canceled_detail", renderer='altairsite.smartphone:templates/page/canceled_detail.html')
    def move_canceled(self):
        canceled_events = self.context.getInfo(kind="canceled", system_tag_id=None)

        return {
              'helper':SmartPhoneHelper()
            , 'canceled_events':canceled_events
        }

    @usersite_view_config(match_param="kind=help", renderer='altairsite.smartphone:templates/page/help.html')
    def move_help(self):
        helps = self.context.getInfo(kind="help", system_tag_id=None)

        return {
              'helps':helps
            , 'helper':SmartPhoneHelper()
        }





    @usersite_view_config(match_param="kind=company", renderer='altairsite.smartphone:templates/page/company.html')
    def move_company(self):
        return {}

    @usersite_view_config(match_param="kind=inquiry", renderer='altairsite.smartphone:templates/page/inquiry.html')
    def move_inquiry(self):
        return {}

    @usersite_view_config(match_param="kind=privacy", renderer='altairsite.smartphone:templates/page/privacy.html')
    def move_privacy(self):
        return {}

    @usersite_view_config(match_param="kind=legal", renderer='altairsite.smartphone:templates/page/legal.html')
    def move_legal(self):
        return {}
