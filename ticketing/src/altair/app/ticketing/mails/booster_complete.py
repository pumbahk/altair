# -*- coding:utf-8 -*-
from .api import create_or_update_mailinfo,  create_fake_order, get_mail_setting_default, get_appropriate_message_part
from .forms import SubjectInfoRenderer, OrderInfoDefault, SubjectInfoWithValue
from mako.template import Template
from altair.app.ticketing.cart import helpers as ch ##
import logging
logger = logging.getLogger(__name__)

from pyramid.renderers import render
from pyramid_mailer.message import Message
from pyramid.compat import text_type
from .interfaces import IPurchaseInfoMail
from zope.interface import implementer
from collections import namedtuple
import traceback
import sys

SubjectInfo = namedtuple("SubjectInfo", "name label getval")

class BoosterOrderCompleteInfoDefault(OrderInfoDefault):
    template_body = SubjectInfoWithValue(name="template_body",  label=u"テンプレート", value="", getval=(lambda order : ""))

    def get_cont(order):
        cont = ""
        old_id_number = ""
        for product in order.ordered_products:
            for item in product.ordered_product_items:
                if "cont" in item._attributes:
                    if item._attributes['cont'].value == "yes":
                        cont = u"継続会員様"
                    else:
                        cont = u"新規会員様"
                if "old_id_number" in item._attributes:
                    if item._attributes['old_id_number'].value:
                        old_id_number = u"昨年度会員番号" + item._attributes['old_id_number'].value

        ret = cont
        if old_id_number:
            ret = cont + u"\n(" + old_id_number + ")"
        return ret

    cont = SubjectInfo(name=u"cont", label=u"新規／継続", getval=get_cont)

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
                mail = BoosterPurchaseCompleteMail(None)
                payment_id, delivery_id = 1, 1 #xxx
                fake_order = create_fake_order(request, request.context.user.organization, payment_id, delivery_id)
                traverser = mutil.get_traverser(request, fake_order)
                mail.build_mail_body(request, fake_order, traverser, template_body=template_body)
                ##xx:
            except Exception as e:
                etype, value, tb = sys.exc_info()
                exc_message = ''.join(traceback.format_exception(etype, value, tb, 10)).replace("\n", "<br/>")
                form.template_body.errors[exc_message] = [exc_message] ##xxx.
                logger.exception(str(e))
                return False
        return True

class BoosterSubjectInfoRenderer(SubjectInfoRenderer):

    def get(self, k):
        return super(BoosterSubjectInfoRenderer, self).get(k)

def get_mailtype_description():
    return u"購入完了メール"

def get_subject_info_default():
    return BoosterOrderCompleteInfoDefault
   
@implementer(IPurchaseInfoMail)
class BoosterPurchaseCompleteMail(object):
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
        info_renderder = BoosterSubjectInfoRenderer(order, traverser.data, default_impl=get_subject_info_default())
        value = dict(h=ch, 
                     order=order,
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

    def build_mail_body(self, request, order, traverser, template_body=None):
        value = self._body_tmpl_vars(request, order, traverser)
        template_body = template_body or value.get("template_body")
        try:
            if template_body and template_body.get("use") and template_body.get("value"):
                value = build_value_with_render_event(request, value)
                return Template(template_body["value"]).render(**value)
            else:
                retval = render(self.mail_template, value, request=request)
                assert isinstance(retval, text_type)
                return retval
        except:
            logger.error("failed to render mail body (template_body=%s)" % template_body)
            raise


from pyramid.interfaces import IRendererGlobalsFactory
from pyramid.events import BeforeRender
def build_value_with_render_event(request, value, system_values=None):
    if system_values is None:
        system_values = {
            'view':None,
            'renderer_name':"*dummy", # b/c
            'renderer_info':"*dummy",
#            'context':getattr(request, 'context', None),
            'request':request,
            'req':request,
            }
    system_values = BeforeRender(system_values, value)
    registry = request.registry
    globals_factory = registry.queryUtility(IRendererGlobalsFactory)

    if globals_factory is not None:
        renderer_globals = globals_factory(system_values)
        if renderer_globals:
            system_values.update(renderer_globals)

    registry.notify(system_values)
    system_values.update(value)
    return system_values
