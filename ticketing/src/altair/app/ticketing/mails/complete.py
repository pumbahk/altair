# -*- coding:utf-8 -*-
import sys
import logging
import traceback
from mako.template import Template
from pyramid.renderers import render
from pyramid_mailer.message import Message
from pyramid.compat import text_type
from zope.interface import implementer
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.cart import helpers as ch ##
from altair.app.ticketing.core import models as c_models
from .api import create_or_update_mailinfo,  create_fake_order, get_mail_setting_default, get_appropriate_message_part, create_mail_request
from .forms import SubjectInfoRenderer, OrderInfoDefault, SubjectInfoWithValue, SubjectInfo
from .interfaces import IPurchaseInfoMail, ICompleteMailResource
from .resources import MailForOrderContext
from .utils import build_value_with_render_event, unescape

logger = logging.getLogger(__name__)

class OrderCompleteInfoDefault(OrderInfoDefault):
    template_body = SubjectInfoWithValue(name="template_body",  label=None, form_label=u"テンプレート", value="", getval=(lambda request, order : ""), use=False)
    payment_method = SubjectInfo(name=u"payment_method", form_label=u"支払方法", label=u"お支払", getval=lambda request, order: order.payment_delivery_pair.payment_method.name)
    delivery_method = SubjectInfo(name=u"delivery_method", form_label=u"引取方法", label=u"お引取", getval=lambda request, order: order.payment_delivery_pair.delivery_method.name)

    @classmethod
    def validate(cls, form, request, mutil):
        data = form.data

        ## template_bodyが渡された場合には実際にレンダリングしてシミュレート
        template_body = data.get("template_body")
        if template_body and template_body.get("use"):
            if not template_body.get("value"):
                ## templateが空文字の時はuse = Falseとして扱う
                form.template_body.use.data = False
                return True
            try:
                mail = PurchaseCompleteMail(None)
                payment_id, delivery_id = 1, 1 #xxx
                fake_order = create_fake_order(request, request.context.organization, payment_id, delivery_id)
                traverser = mutil.get_traverser(request, fake_order)
                mail.build_mail_body(request, fake_order, traverser, template_body=template_body)
                ##xx:
            except Exception as e:
                etype, value, tb = sys.exc_info()
                exc_message = ''.join(traceback.format_exception(etype, value, tb, 10)).replace("\n", "<br/>")
                form.template_body.errors = list(form.template_body.errors) + [exc_message] ##xxx.
                logger.exception(str(e))
                return False
        return True

def get_mailtype_description():
    return u"購入完了メール"

def get_subject_info_default():
    return OrderCompleteInfoDefault
  

@implementer(ICompleteMailResource)
class PurchaseCompleteMailResource(MailForOrderContext):
    """ 完了メール """
    mtype = c_models.MailTypeEnum.PurchaseCompleteMail


@implementer(IPurchaseInfoMail)
class PurchaseCompleteMail(object):
    def __init__(self, mail_template):
        self.mail_template = mail_template

    def get_mail_subject(self, request, organization, traverser):
        return (traverser.data["subject"] or 
                u"チケット予約受付完了のお知らせ 【{organization}】".format(organization=organization.name))
        
    def build_message_from_mail_body(self, request, order, traverser, mail_body):
        organization = order.ordered_from or request.organization
        mail_setting_default = get_mail_setting_default(request)
        subject = self.get_mail_subject(request, organization, traverser)
        sender = mail_setting_default.get_sender(request, traverser, organization)
        bcc = mail_setting_default.get_bcc(request, traverser, organization)
        return Message(
            subject=subject,
            recipients=[order.shipping_address.email_1],
            bcc=bcc,
            body=get_appropriate_message_part(request, order.shipping_address.email_1, mail_body),
            sender=sender)

    def build_message(self, request, subject, traverser):
        mail_body = self.build_mail_body(request, subject, traverser)
        return self.build_message_from_mail_body(request, subject, traverser, mail_body)
        
    def _body_tmpl_vars(self, request, order, traverser):
        sa = order.shipping_address 
        pair = order.payment_delivery_pair
        info_renderder = SubjectInfoRenderer(request, order, traverser.data, default_impl=get_subject_info_default())
        value = dict(h=ch, 
                     order=order,
                     extra_form_data=order.get_order_attribute_pair_pairs(request, mode='entry'),
                     get=info_renderder.get, 
                     name=u"{0} {1}".format(sa.last_name, sa.first_name),
                     payment_method_name=pair.payment_method.name, 
                     delivery_method_name=pair.delivery_method.name, 
                     ### mail info
                     footer = traverser.data["footer"],
                     notice = traverser.data["notice"],
                     header = traverser.data["header"],
                     template_body = traverser.data["template_body"] #xxxx:
                     )
        return value

    def build_mail_body(self, request, order, traverser, template_body=None, kind='plain'):
        organization = order.organization
        mail_request = create_mail_request(request, organization, lambda request: PurchaseCompleteMailResource(request, order))
        value = self._body_tmpl_vars(mail_request, order, traverser)
        template_body = template_body or value.get("template_body")
        try:
            if template_body and template_body.get("use") and template_body.get("value"):
                value = build_value_with_render_event(mail_request, value, context=mail_request.context)
                retval = Template(template_body["value"], default_filters=['h']).render(**value)
            else:
                cart_setting = cart_api.get_cart_setting_from_order_like(request, order)
                mail_template = self.mail_template % dict(cart_type=(cart_setting.type if cart_setting is not None else 'standard'))
                retval = render(mail_template, value, request=mail_request)
            assert isinstance(retval, text_type)
            if kind == 'plain':
                retval = unescape(retval)
            return retval
        except:
            logger.error("failed to render mail body (template_body=%s)" % template_body)
            raise
