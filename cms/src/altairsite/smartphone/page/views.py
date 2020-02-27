# -*- coding:utf-8 -*-
from datetime import datetime

from altairsite.config import smartphone_site_view_config
from altairsite.inquiry.api import send_inquiry_mail
from altairsite.inquiry.message import CustomerMailRT, SupportMailRT, CustomerMailST, SupportMailST
from altairsite.inquiry.session import InquirySession
from altairsite.separation import selectable_renderer
from pyramid.view import view_defaults

from .forms import RtInquiryForm, StInquiryForm
from ..common.helper import SmartPhoneHelper


@view_defaults(route_name="smartphone.page",request_type="altair.mobile.interfaces.ISmartphoneRequest")
class StaticKindView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @smartphone_site_view_config(match_param="kind=orderreview", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/orderreview.html'))
    def move_orderreview(self):
        orderreview_url = self.context.get_orderreview_url()
        return {
            'orderreview_url':orderreview_url
        }

    @smartphone_site_view_config(match_param="kind=canceled", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/canceled.html'))
    def move_canceled(self):
        canceled_topics = self.context.getInfo(kind="canceled", system_tag_id=None)

        return {
              'helper':SmartPhoneHelper()
            , 'canceled_topics':canceled_topics
            , 'sns':{
                'url':"https://ticket.rakuten.co.jp/change",
                'title':u"楽天チケット-公演中止・変更情報"
            }
        }

    @smartphone_site_view_config(match_param="kind=canceled_detail", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/canceled_detail.html'))
    def move_canceled_detail(self):
        topicid = self.request.GET['topic_id']
        canceled_topic = self.context.get_canceled_topic(topicid)

        return {
              'helper':SmartPhoneHelper()
            , 'canceled_topic':canceled_topic
            , 'sns':{
                'url':"https://ticket.rakuten.co.jp/change",
                'title':u"楽天チケット-公演中止・変更情報"
            }
        }

    @smartphone_site_view_config(match_param="kind=help", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/help.html'))
    def move_help(self):
        helps = self.context.getInfo(kind="help", system_tag_id=None)

        return {
              'helps':helps
            , 'helper':SmartPhoneHelper()
            , 'sns':{
                'url':"https://ktohoku.tstar.jp/faq",
                'title':u"キョードー東北モバイルチケット-FAQ"
            }
        }

    @smartphone_site_view_config(match_param="kind=company", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/company.html'))
    def move_company(self):
        return {
            'sns':{
                'url':"http://www.ticketstar.jp/",
                'title':u"楽天チケット-運営会社"
            }
        }

    @smartphone_site_view_config(match_param="kind=inquiry", request_method="GET", renderer=selectable_renderer(
        'altairsite.smartphone:templates/%(prefix)s/page/inquiry.html'))
    def move_inquiry(self):
        session = InquirySession(request=self.request)
        session.put_inquiry_session()
        form = get_org_form(self.request)
        form.admission_time.data = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        return {
            'form': form
            , 'sns': {
                'url': "https://ticket.rakuten.co.jp/inquiry",
                'title': u"楽天チケット-お問い合わせ"
            }
        }

    @smartphone_site_view_config(match_param="kind=inquiry", request_method="POST", renderer=selectable_renderer(
        'altairsite.smartphone:templates/%(prefix)s/page/inquiry.html'))
    def move_inquiry_post(self):
        form = get_org_form(self.request)
        session = InquirySession(request=self.request)
        if not session.exist_inquiry_session():
            return {
                "form": form,
                "result": True
            }

        if not form.validate():
            return {"form": form}

        ret = send_inquiry_mail_org(self.request)

        session.delete_inquiry_session()

        return {
            'form': form
            , 'result': ret
            , 'sns': {
                'url': "https://ticket.rakuten.co.jp/inquiry",
                'title': u"楽天チケット-お問い合わせ"
            }
        }

    @smartphone_site_view_config(match_param="kind=privacy", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/privacy.html'))
    def move_privacy(self):
        return {
            'sns':{
                'url':"http://privacy.rakuten.co.jp/",
                'title':u"楽天チケット-個人情報保護方針"
            }
        }

    @smartphone_site_view_config(match_param="kind=legal", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/legal.html'))
    def move_legal(self):
        return {
            'sns':{
                'url':"http://www.ticketstar.jp/legal",
                'title':u"楽天チケット-特定商取引法に基づく表示"
            }
        }

    @smartphone_site_view_config(match_param="kind=purchase", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/purchase.html'))
    def move_purchase(self):
        return {
            'sns':{
                'url':"http://ktohoku.tstar.jp/purchase",
                'title':u"キョードー東北モバイルチケット-購入方法"
            }
        }

    @smartphone_site_view_config(match_param="kind=information", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/information.html'))
    def move_information(self):
        return {}

    @smartphone_site_view_config(match_param="kind=mente", renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/page/mente.html'))
    def move_mente(self):
        return {}


def get_org_form(request):
    form = None

    if request.organization.short_name == "RT":
        form = RtInquiryForm(request.POST)

    if request.organization.short_name == "ST":
       form = StInquiryForm(request.POST)

    return form

def send_inquiry_mail_org(request):
    ret = True

    if request.organization.short_name == "RT":
        ret = send_inquiry_mail_rt(request)

    if request.organization.short_name == "ST":
        ret = send_inquiry_mail_st(request)

    return ret

def send_inquiry_mail_rt(request):
    form = RtInquiryForm(request.POST)
    ret = True

    customer_mail = CustomerMailRT(form.data['username'], form.data['username_kana'], form.data['zip_no']
                                 , form.data['address'], form.data['tel'], form.data['mail'], form.data['reception_number'],
                                 form.data['category']
                                 , form.data['title'], form.data['body'])
    support_mail = SupportMailRT(form.data['username'], form.data['username_kana'], form.data['zip_no']
                               , form.data['address'], form.data['tel'], form.data['mail'], form.data['reception_number'],
                               form.data['category']
                               , form.data['title'], form.data['body'], request.environ.get("HTTP_USER_AGENT"))

    ret = send_inquiry_mail(request=request, title=u"楽天チケット　お問い合わせフォーム[PC]", body=support_mail.create_mail(),
                      recipients=[request.inquiry_mailaddress])
    if ret:
        ret = send_inquiry_mail(request=request, title=u"楽天チケット　お問い合わせ", body=customer_mail.create_mail(),
                            recipients=[form.mail.data])
    return ret


def send_inquiry_mail_st(request):
    form = StInquiryForm(request.POST)
    ret = True

    customer_mail = CustomerMailST(form.data['username'], form.data['username_kana'], form.data['mail']
                                 , form.data['zip_no'], form.data['address'], form.data['tel']
                                 , form.data['reception_number'], form.data['app_status'], form.data['event_name']
                                 , form.data['start_date'], form.data['category'], form.data['body'])

    support_mail = SupportMailST(form.data['username'], form.data['username_kana'], form.data['mail']
                                 , form.data['zip_no'], form.data['address'], form.data['tel']
                                 , form.data['reception_number'], form.data['app_status'], form.data['event_name']
                                 , form.data['start_date'], form.data['category'], form.data['body'], request.environ.get("HTTP_USER_AGENT"))

    ret = send_inquiry_mail(request=request, title=u"SMAチケット　お問い合わせフォーム[PC]", body=support_mail.create_mail(),
                      recipients=[request.inquiry_mailaddress])
    if ret:
        ret = send_inquiry_mail(request=request, title=u"SMAチケット　お問い合わせ", body=customer_mail.create_mail(),
                            recipients=[form.mail.data])
    return ret
