# -*- coding:utf-8 -*-
from .forms import InquiryForm
from ..common.helper import SmartPhoneHelper
from altairsite.config import smartphone_site_view_config
from altairsite.inquiry.message import CustomerMail, SupportMail
from altairsite.inquiry.api import send_inquiry_mail
from altairsite.inquiry.session import InquirySession
from altairsite.separation import selectable_renderer
from pyramid.view import view_defaults

@view_defaults(route_name="smartphone.page",request_type="altairsite.tweens.ISmartphoneRequest")
class StaticKindView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @smartphone_site_view_config(match_param="kind=orderreview", renderer=selectable_renderer('altairsite.smartphone:templates/page/orderreview.html'))
    def move_orderreview(self):
        orderreview_url = self.context.get_orderreview_url()
        return {
            'orderreview_url':orderreview_url
        }

    @smartphone_site_view_config(match_param="kind=canceled", renderer=selectable_renderer('altairsite.smartphone:templates/page/canceled.html'))
    @smartphone_site_view_config(match_param="kind=canceled_detail", renderer=selectable_renderer('altairsite.smartphone:templates/page/canceled_detail.html'))
    def move_canceled(self):
        canceled_events = self.context.getInfo(kind="canceled", system_tag_id=None)

        return {
              'helper':SmartPhoneHelper()
            , 'canceled_events':canceled_events
            , 'sns':{
                'url':"https://ticket.rakuten.co.jp/change",
                'title':u"楽天チケット-公演中止・変更情報"
            }
        }

    @smartphone_site_view_config(match_param="kind=help", renderer=selectable_renderer('altairsite.smartphone:templates/page/help.html'))
    def move_help(self):
        helps = self.context.getInfo(kind="help", system_tag_id=None)

        return {
              'helps':helps
            , 'helper':SmartPhoneHelper()
            , 'sns':{
                'url':"https://ticket.rakuten.co.jp/faq",
                'title':u"楽天チケット-よくある質問"
            }
        }

    @smartphone_site_view_config(match_param="kind=company", renderer=selectable_renderer('altairsite.smartphone:templates/page/company.html'))
    def move_company(self):
        return {
            'sns':{
                'url':"http://www.ticketstar.jp/",
                'title':u"楽天チケット-運営会社"
            }
        }

    @smartphone_site_view_config(match_param="kind=inquiry", request_method="GET", renderer=selectable_renderer('altairsite.smartphone:templates/page/inquiry.html'))
    def move_inquiry(self):
        session = InquirySession(request=self.request)
        session.put_inquiry_session();
        return {
            'form':InquiryForm()
            , 'sns':{
                'url':"https://ticket.rakuten.co.jp/inquiry",
                'title':u"楽天チケット-お問い合わせ"
            }
        }

    @smartphone_site_view_config(match_param="kind=inquiry", request_method="POST", renderer=selectable_renderer('altairsite.smartphone:templates/page/inquiry.html'))
    def move_inquiry_post(self):
        form = InquiryForm(self.request.POST)

        session = InquirySession(request=self.request)
        if not session.exist_inquiry_session():
            return {
                "form": form,
                "result": True
            }

        if not form.validate():
            return {"form": form}

        customer_mail = CustomerMail(form.data['username'], form.data['mail'], form.data['num'], form.data['category']
            , form.data['title'], form.data['body'])
        support_mail = SupportMail(form.data['username'], form.data['mail'], form.data['num'], form.data['category']
            , form.data['title'], form.data['body'], self.request.environ.get("HTTP_USER_AGENT"))

        send_inquiry_mail(request=self.request, title=u"楽天チケット　お問い合わせフォーム[スマホ]", body=support_mail.create_mail(), recipients=[self.request.inquiry_mailaddress])
        ret = send_inquiry_mail(request=self.request, title=u"楽天チケット　お問い合わせ", body=customer_mail.create_mail(), recipients=[form.mail.data])

        session.delete_inquiry_session()

        return {
             'form':form
            ,'result':ret
            , 'sns':{
                'url':"https://ticket.rakuten.co.jp/inquiry",
                'title':u"楽天チケット-お問い合わせ"
            }
        }

    @smartphone_site_view_config(match_param="kind=privacy", renderer=selectable_renderer('altairsite.smartphone:templates/page/privacy.html'))
    def move_privacy(self):
        return {
            'sns':{
                'url':"http://privacy.rakuten.co.jp/",
                'title':u"楽天チケット-個人情報保護方針"
            }
        }

    @smartphone_site_view_config(match_param="kind=legal", renderer=selectable_renderer('altairsite.smartphone:templates/page/legal.html'))
    def move_legal(self):
        return {
            'sns':{
                'url':"http://www.ticketstar.jp/legal",
                'title':u"楽天チケット-特定商取引法に基づく表示"
            }
        }

    @smartphone_site_view_config(match_param="kind=information", renderer=selectable_renderer('altairsite.smartphone:templates/page/information.html'))
    def move_information(self):
        return {}
