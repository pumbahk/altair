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
import traceback
import sys

class OrderCompleteInfoDefault(OrderInfoDefault):
    template_body = SubjectInfoWithValue(name="template_body",  label=u"テンプレート", value="", getval=(lambda order : ""))

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
                mail = PurchaseCompleteMail(None, request)
                payment_id, delivery_id = 1, 1 #xxx
                fake_order = create_fake_order(request, request.context.user.organization, payment_id, delivery_id)
                traverser = mutil.get_traverser(request, fake_order)
                mail.build_mail_body(fake_order, traverser, template_body=template_body)
                ##xx:
            except Exception as e:
                etype, value, tb = sys.exc_info()
                exc_message = ''.join(traceback.format_exception(etype, value, tb, 10)).replace("\n", "<br/>")
                form.template_body.errors[exc_message] = [exc_message] ##xxx.
                logger.exception(str(e))
                return False
        return True

def get_mailtype_description():
    return u"購入完了メール"

def get_subject_info_default():
    return OrderCompleteInfoDefault
   
@implementer(IPurchaseInfoMail)
class PurchaseCompleteMail(object):
    def __init__(self, mail_template, request):
        self.mail_template = mail_template
        self.request = request

    def get_mail_subject(self, organization, traverser):
        return (traverser.data["subject"] or 
                u"チケット予約受付完了のお知らせ 【{organization}】".format(organization=organization.name))
        
    def build_message_from_mail_body(self, order, traverser, mail_body):
        organization = order.ordered_from or self.request.organization
        mail_setting_default = get_mail_setting_default(self.request)
        subject = self.get_mail_subject(organization, traverser)
        sender = mail_setting_default.get_sender(self.request, traverser, organization)
        bcc = mail_setting_default.get_bcc(self.request, traverser, organization)
        return Message(
            subject=subject,
            recipients=[order.shipping_address.email_1],
            bcc=bcc,
            body=get_appropriate_message_part(self.request, order.shipping_address.email_1, mail_body),
            sender=sender)

    def build_message(self, subject, traverser):
        mail_body = self.build_mail_body(subject, traverser)
        return self.build_message_from_mail_body(subject, traverser, mail_body)
        
    def _body_tmpl_vars(self, order, traverser):
        sa = order.shipping_address 
        pair = order.payment_delivery_pair
        info_renderder = SubjectInfoRenderer(order, traverser.data, default_impl=get_subject_info_default())
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

    def build_mail_body(self, order, traverser, template_body=None):
        value = self._body_tmpl_vars(order, traverser)
        template_body = template_body or value.get("template_body")
        try:
            if template_body and template_body.get("use") and template_body.get("value"):
                value = build_value_with_render_event(self.request, value)
                return Template(template_body["value"]).render(**value)
            else:
                retval = render(self.mail_template, value, request=self.request)
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

