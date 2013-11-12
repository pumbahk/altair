# -*- coding:utf-8 -*-
from pyramid.renderers import render
from pyramid_mailer.message import Message
from pyramid.compat import text_type
import logging
from .forms import SubjectInfoRenderer, RenderVal
from .forms import OrderInfoDefaultMixin, SubjectInfoDefaultBase, SubjectInfo, SubjectInfoWithValue
from altair.app.ticketing.cart import helpers as ch ##
from altair.app.ticketing.loyalty.models import PointGrantStatusEnum, PointGrantHistoryEntry
from .interfaces import IPointGrantHistoryEntryInfoMail
from zope.interface import implementer
from .api import create_or_update_mailinfo, get_mail_setting_default, get_appropriate_message_part

logger = logging.getLogger(__name__)

class PointGrantingFailureInfoDefault(SubjectInfoDefaultBase, OrderInfoDefaultMixin):
    failure_reasons = {
        PointGrantStatusEnum.InvalidPointAccountNumber.v:
            u'ポイント口座番号に誤りがあるため',
        PointGrantStatusEnum.NoSuchPointAccount.v:
            u'ポイント口座番号に誤りがあるため',
        }

    def get_contact(order):
        return u"""\
%s
商品、決済・発送に関するお問い合わせ %s""" % (order.ordered_from.name, order.ordered_from.contact_email)
    contact = SubjectInfo(name=u"contact", label=u"お問い合わせ", getval=get_contact)

    def failure_reason_default(point_grant_history_entry):
        reason = PointGrantingFailureInfoDefault.failure_reasons.get(point_grant_history_entry.grant_status)
        if reason is None:
            # 実際には事前にバリデーションしているのでここに飛んでくることはない
            return u'その他の理由で'
        else:
            return reason

    ## getvalが文字列の場合は、input formになり文言を変更できる
    failure_reason = SubjectInfoWithValue(name="failure_reason", label=u"付与失敗理由", getval=failure_reason_default, value=u"")

def get_subject_info_default():
    return PointGrantingFailureInfoDefault()

def get_mailtype_description():
    return u"ポイント付与失敗"

class PointGrantHistoryEntryInfoRenderer(SubjectInfoRenderer):
    def __init__(self, point_grant_history_entry, data, default_impl):
        super(PointGrantHistoryEntryInfoRenderer, self).__init__(
            point_grant_history_entry.order,
            data,
            default_impl)
        self.point_grant_history_entry = point_grant_history_entry

    def _get(self, k):
        if not hasattr(self, k):
            val = self.data and self.data.get(k)
            if not val:
                default_val = getattr(self.default, k, None)
                if default_val:
                    setattr(self, k, RenderVal(label=default_val.label, status=True, body=default_val.getval(self.point_grant_history_entry)))
                else:
                    setattr(self, k, RenderVal(label="", status=False, body=u""))                    
            elif val["use"]:
                setattr(self, k, RenderVal(label=val["kana"], status=True, 
                                           body=val.get("value") or getattr(self.default, k).getval(self.point_grant_history_entry)))
            else:
                setattr(self, k, RenderVal(label="", status=False, body=getattr(val, "body", u"")))
        return getattr(self, k)

    def get(self, k):
        if k == 'failure_reason':
            return self._get(k)
        else: 
            return super(PointGrantHistoryEntryInfoRenderer, self).get(k)


@implementer(IPointGrantHistoryEntryInfoMail)    
class PointGrantingFailureMail(object):
    def __init__(self, mail_template):
        self.mail_template = mail_template

    def get_mail_subject(self, request, organization, traverser):
        return (traverser.data["subject"] or 
                u'楽天スーパーポイント付与に関するご案内【{organization}】'.format(organization=organization.name))

    def get_mail_sender(self, request, organization, traverser):
        return (traverser.data["sender"] or organization.contact_email)

    def validate(self, point_grant_history_entry):
        retval = []
        if point_grant_history_entry.grant_status not in (
            PointGrantStatusEnum.InvalidPointAccountNumber.v,
            PointGrantStatusEnum.NoSuchPointAccount.v):
            retval.append('PointGrantHistoryEntry(id=%d) does not have valid grant_status assigned (status=%s)' % (point_grant_history_entry.id, point_grant_history_entry.grant_status))
        order = point_grant_history_entry.order
        if order.shipping_address is None or not order.shipping_address.email_1:
            retval.append('order(%d) has no shipping_address or email' % order.id)
        return retval

    def build_message(self, request, subject, traverser):
        mail_body = self.build_mail_body(request, subject, traverser)
        return self.build_message_from_mail_body(request, subject, traverser, mail_body)

    def build_message_from_mail_body(self, request, point_grant_history_entry, traverser, mail_body):
        errors = self.validate(point_grant_history_entry)
        if errors:
            logger.warn("validation error: %s" % ' / '.join(errors))
            return None
        order = point_grant_history_entry.order
        organization = order.ordered_from or request.context.organization
        mail_setting_default = get_mail_setting_default(request)
        subject = self.get_mail_subject(request, organization, traverser)
        sender = mail_setting_default.get_sender(request, traverser, organization)
        bcc = mail_setting_default.get_bcc(request, traverser, organization)
        primary_recipient = order.shipping_address.email_1 if order.shipping_address else None
        return Message(
            subject=subject,
            recipients=[primary_recipient] if primary_recipient else [],
            bcc=bcc,
            body=get_appropriate_message_part(request, primary_recipient, mail_body),
            sender=sender)

    def _body_tmpl_vars(self, request, point_grant_history_entry, traverser):
        order = point_grant_history_entry.order
        sa = order.shipping_address 
        info_renderder = PointGrantHistoryEntryInfoRenderer(point_grant_history_entry, traverser.data, default_impl=PointGrantingFailureInfoDefault)
        title = order.performance.event.title
        pair = order.payment_delivery_pair
        value = dict(h=ch, 
                     order=order,
                     title=title, 
                     get=info_renderder.get,
                     name=u"{0} {1}".format(sa.last_name, sa.first_name) if sa else u"inner", 
                     point_submitted_on=point_grant_history_entry.submitted_on,
                     point_amount=point_grant_history_entry.amount,
                     payment_method_name=pair.payment_method.name, 
                     delivery_method_name=pair.delivery_method.name, 
                     ### mail info
                     footer = traverser.data["footer"],
                     notice = traverser.data["notice"],
                     header = traverser.data["header"],
                     )
        return value

    def build_mail_body(self, request, point_grant_history_entry, traverser):
        value = self._body_tmpl_vars(request, point_grant_history_entry, traverser)
        retval = render(self.mail_template, value, request=request)
        assert isinstance(retval, text_type)
        return retval
