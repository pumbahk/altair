# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

import itertools
from altair.formhelpers.form import OurForm
from altair.formhelpers import fields
from altair.formhelpers import widgets
from wtforms import validators
from collections import namedtuple, OrderedDict
from altair.app.ticketing.cart import helpers as ch


class SubjectInfo(object):
    def __init__(self, name, label, getval, form_label=None, use=True):
        self.name = name
        self.label = label
        self.getval = getval
        self.form_label = form_label or label
        self.use = use

class SubjectInfoWithValue(object):
    def __init__(self, name, label, getval, value, form_label=None, use=True):
        self.name = name
        self.label = label
        self.getval = getval
        self.value = value
        self.form_label = form_label or label
        self.use = use

RenderVal = namedtuple("RenderVal", "status label, body")
PluginInfo = namedtuple("PluginInfo", "method name label") #P0, P0notice, 注意事項(コンビニ決済)

class SubjectInfoForm(OurForm):
    use = fields.OurBooleanField(u"有効にする")
    kana = fields.OurTextField(u"ラベル名", validators=[validators.Required()])

class SubjectInfoWithValueForm(OurForm):
    use = fields.OurBooleanField(u"有効にする")
    kana = fields.OurTextField(u"ラベル名", validators=[validators.Optional()])
    value = fields.OurTextField(label=u"内容", widget=widgets.OurTextArea(), 
                             validators=[validators.Optional()])

class SubjectInfoWithValueButLabelForm(OurForm):
    use = fields.OurBooleanField(u"有効にする")
    value = fields.OurTextField(label=u"内容", widget=widgets.OurTextArea(), 
                             validators=[validators.Optional()])

class SubjectInfoDefaultBase(object):
    @classmethod
    def get_form_field_candidates(cls):
        hist = {}
        for c in cls.__mro__:
            for k, v in c.__dict__.iteritems():
                if isinstance(v, (SubjectInfo, SubjectInfoWithValue)) and not k in hist:
                    hist[k] = 1
                    yield (k, v)

class SubjectInfoDefaultMixin(object):
    ## subject = order or lots_entry
    def get_name_kana(request, subject):
        sa = subject.shipping_address
        if sa is None:
            return u""
        return u"{0} {1}".format(sa.last_name_kana, sa.first_name_kana)

    name_kana = SubjectInfo(name="name_kana", label=u"お名前カナ", getval=get_name_kana)
    tel = SubjectInfo(name="tel", label=u"電話番号", getval=lambda request, subject : subject.shipping_address.tel_1 or "" if subject.shipping_address else u"")
    mail = SubjectInfo(name="mail", label=u"メールアドレス", getval=lambda request, subject : subject.shipping_address.email_1 if subject.shipping_address else u"")
    order_datetime = SubjectInfo(name="order_datetime", label=u"受付日", getval=lambda request, order: ch.mail_date(order.created_at))
    bcc = SubjectInfoWithValue(name="bcc", label=None, form_label=u"bcc", getval=lambda request, order: None, value=None)
   

def sensible_text_coerce(v):
    if v is None:
        return u'(回答なし)'
    elif isinstance(v, list):
        if len(v) == 0:
            return u'(選択なし)'
        else:
            return u', '.join(v)
    else:
        return v

class OrderInfoDefaultMixin(object):
    """ 
    以下の情報のデフォルトの値。ラベル名が変えられ、表示するかしないか選択できる。
    #注文情報 受付番号、受付日時、公演タイトル、商品名、座席番号、商品代金、サービス利用料・手数料、合計金額
    """
    def get_event_title(request, order):
        performance = order.performance
        return u"{0} {1}".format(performance.event.title, performance.name)

    def get_performance_date(request, order):
        if order.performance.end_on:
            o = order.performance.start_on
            c = order.performance.end_on
            period = ch.japanese_date(o) + u'〜' + ch.japanese_date(c)
            if o.year==c.year and o.month==c.month and o.day==c.day:
                period = ch.japanese_datetime(o)
        else:
            period = ch.japanese_datetime(order.performance.start_on)
        return period

    def get_seat_no(request, order):
        seat_no = []
        for p in order.items:
            # XXX: seat_stock_type を使っているのは券種のときに直すとしても、
            # なぜこれ、product をイテレートしている場所で席種を表示したいのだ?
            if p.seats:
                if p.product.sales_segment.setting.display_seat_no:
                    seat_no += [u"* {0}".format(seat["name"]) for seat in p.seats]
                elif p.product.seat_stock_type is not None:
                    seat_no += [u"{0} {1}席".format(p.product.name, p.seat_quantity)]
            else:
                if p.product.seat_stock_type.is_seat:
                    seat_no += [u"{0} {1}席".format(p.product.name, p.seat_quantity)]
                else:
                    seat_no += [u"{0} x{1}".format(p.product.name, p.quantity)]
                
        return u"\n".join(seat_no)

    def get_product_description(request, order):
        return u"\n".join((u"{0} {1} x{2}".format(op.product.name,
                                                    ch.format_currency(op.product.price),
                                                    op.quantity)
                           for op in order.items))

    def get_extra_form_data(request, order):
        return u"\n".join(
            u"【{0}】{1}".format(pair[1][0], sensible_text_coerce(pair[1][1]))
            for pair in order.get_order_attribute_pair_pairs(request, mode='entry')
            )

    order_no = SubjectInfo(name="order_no", label=u"受付番号", getval=lambda request, subject : subject.order_no)
    event_name = SubjectInfo(name=u"event_name", label=u"公演タイトル", getval=get_event_title)
    pdate = SubjectInfo(name=u"pdate", label=u"公演日時", getval=get_performance_date)
    venue = SubjectInfo(name=u"venue", label=u"会場", getval=lambda request, order: order.performance.venue.name)
    for_product =SubjectInfo(name=u"for_product", label=u"商品代金", getval=get_product_description)
    for_seat = SubjectInfo(name=u"for_seat", label=u"ご購入いただいた座席", getval=get_seat_no)
    system_fee = SubjectInfo(name=u"system_fee", label=u"システム利用料", getval=lambda request, order: ch.format_currency(order.system_fee))
    special_fee = SubjectInfo(name=u'special_fee', label=u'特別手数料', getval=lambda request, order: ch.format_currency(order.special_fee))
    special_fee_name = SubjectInfo(name=u'special_fee_name', label=u'特別手数料名', getval=lambda request, order: order.special_fee_name)        
    transaction_fee = SubjectInfo(name=u"transaction_fee", label=u"決済手数料", getval=lambda request, order: ch.format_currency(order.transaction_fee))
    delivery_fee = SubjectInfo(name=u"delivery_fee", label=u"発券／引取手数料", getval=lambda request, order: ch.format_currency(order.delivery_fee))
    total_amount = SubjectInfo(name=u"total_amount", label=u"合計金額", getval=lambda request, order: ch.format_currency(order.total_amount))
    extra_form_data = SubjectInfo(name=u"extra_form_data", label=u"追加情報", getval=get_extra_form_data)

class SubjectInfoDefault(SubjectInfoDefaultBase, SubjectInfoDefaultMixin):
    pass

class OrderInfoDefault(SubjectInfoDefaultBase, SubjectInfoDefaultMixin, OrderInfoDefaultMixin):
    pass

class SubjectInfoRenderer(object):
    def __init__(self, request, order, data, default_impl=SubjectInfoDefault):
        self.request = request
        self.order = order
        self.data = data
        self.default = default_impl

    def get(self, k):
        if not hasattr(self, k):
            val = self.data and self.data.get(k)
            if not val:
                default_val = getattr(self.default, k, None)
                if default_val:
                    setattr(self, k, RenderVal(label=default_val.label, status=True, body=default_val.getval(self.request, self.order)))
                else:
                    setattr(self, k, RenderVal(label="", status=False, body=u""))                    
            elif val["use"]:
                setattr(self, k, RenderVal(label=val["kana"], status=True, 
                                           body=val.get("value") or getattr(self.default, k).getval(self.request, self.order)))
            else:
                setattr(self, k, RenderVal(label="", status=False, body=getattr(val, "body", u"")))
        return getattr(self, k)


def MailInfoFormFactory(template, mutil=None, request=None):
    attrs = OrderedDict()
    attrs["subject"] = fields.OurTextField(label=u"メール件名")
    attrs["sender"] = fields.OurTextField(label=u"メールsender")

    try:
        default = mutil.get_subject_info_default()
    except:
        logger.warn("mutil is not found. default is SubjectInfoDefault")
        default = SubjectInfoDefault

    for k, v in default.get_form_field_candidates():
        dv = getattr(default, k, None)
        if hasattr(v, "value"):
            if dv is None or dv.label is not None:
                attrs[k] = fields.OurFormField(SubjectInfoWithValueForm, label=v.form_label, 
                                               default=dict(use=v.use, kana=v.label, doc=v, value=v.value)) ##xxx:
            else:
                attrs[k] = fields.OurFormField(SubjectInfoWithValueButLabelForm, label=v.form_label, 
                                               default=dict(use=v.use, doc=v, value=v.value)) ##xxx:
        else:
            attrs[k] = fields.OurFormField(SubjectInfoForm, label=v.form_label, 
                                           default=dict(use=v.use, kana=v.label, doc=v)) ##xxx:

    for e in template.template_keys():
        attrs[e.name] = fields.OurTextField(label=e.label, widget=widgets.OurTextArea(), description=e.method, 
                                            validators=[validators.Optional()])
        
    attrs["payment_types"] = [e[0] for e in template.payment_methods_choices()]
    attrs["delivery_types"] = [e[0] for e in template.delivery_methods_choices()]


    ## validation
    def validate(self): # todo error message
        status = super(type(self), self).validate()
        for k in self.data.keys():
            if k.startswith("P"):
                if not any(p in k for p in attrs["payment_types"]):
                    status = False
            if k.startswith("D"):
                if not any(p in k for p in attrs["delivery_types"]):
                    status = False
        if hasattr(default, "validate"):
            return status and default.validate(self, request=request, mutil=mutil)
        return status
    attrs["validate"] = validate

    def as_mailinfo_data(self):
        return {k:v for k, v in self.data.iteritems()}
    attrs["as_mailinfo_data"] = as_mailinfo_data

    return type("MailInfoForm", (OurForm, ), attrs)

def MethodChoicesFormFactory(template):
    attrs = {}
    choices = [(m.id, m.name) for m in template.organization.payment_method_list]
    attrs["payment_methods"] = fields.OurSelectField(label=u"決済方法", choices=choices, id="payment_methods")    

    choices = [(m.id, m.name) for m in template.organization.delivery_method_list]
    attrs["delivery_methods"] = fields.OurSelectField(label=u"引取方法", choices=choices, id="delivery_methods")
    return type("MethodChoiceForm", (OurForm, ), attrs)


class MailInfoTemplate(object):
    """
    data = {
      "header": u"ヘッダー", 
      "P0header": u"payment_plugin (0)header"
      "P1header": u"payment_plugin (1)header", 
      "D0header": u"deliveery_plugin (0)header"
      "D1header": u"deliveery_plugin (1)header", 
    }
    """
    def as_choice_formclass(self):
        return MethodChoicesFormFactory(self)

    def as_formclass(self):
        return MailInfoFormFactory(self, mutil=self.mutil, request=self.request)

    payment_choices = [#("header", u"ヘッダ"),
                       ("notice", u"決済：注意事項"),
                       #("footer", u"フッタ"),
                       ]
    delivery_choices = [#("header", u"ヘッダー"),
                       ("notice", u"受取：注意事項"),
                       #("footer", u"フッター"),
                       ]
    common_choices = [
        PluginInfo("", "header", u"メールヘッダー"),
        PluginInfo("", "notice", u"共通注意事項"),
        PluginInfo("", "footer", u"メールフッター"),
        ]

    address_choices = [
        PluginInfo("", "inquiry_link", u"お問い合わせ先"),
        PluginInfo("", "history_link", u"購入履歴確認先"),
        PluginInfo("", "magazine_link", u"メールマガジンの配信をご希望される方はこちら"),
    ]

    def __init__(self, request, organization, mutil=None):
        self.request = request
        self.organization = organization
        self.mutil = mutil

    payment_key_fmt = "P%s%s"
    delivery_key_fmt = "D%s%s"

    def payment_methods_choices(self):
        return [("P%d" % m.payment_plugin_id, m.name)
            for m in self.organization.payment_method_list]

    def delivery_methods_choices(self):
        return [("D%d" % m.delivery_plugin_id, m.name)
            for m in self.organization.delivery_method_list]

    def payment_methods_keys(self, payment_id):
        candidates = self.organization.payment_method_list
        if payment_id:
            candidates = (m for m in candidates if m.payment_plugin_id==payment_id) #xxx:

        for payment_method in candidates:
            plugin_id = payment_method.payment_plugin_id
            payment_type = "payment P%d" % plugin_id
            plugin_name = payment_method.payment_plugin.name

            for k, v in self.payment_choices:
                yield PluginInfo(name=self.payment_key_fmt % (plugin_id, k),
                                 method=payment_type, 
                                 label=u"%s(%s)" % (v, plugin_name))
                
                
    def delivery_methods_keys(self, delivery_id):
        candidates = self.organization.delivery_method_list
        if delivery_id:
            candidates = (m for m in candidates if m.delivery_plugin_id==delivery_id) #xxx:
        for delivery_method in candidates:
            plugin_id = delivery_method.delivery_plugin_id
            delivery_type = "delivery D%d" % plugin_id
            plugin_name = delivery_method.delivery_plugin.name

            for k, v in self.delivery_choices:
                yield PluginInfo(name=self.delivery_key_fmt % (plugin_id, k),
                                 method=delivery_type,
                                 label=u"%s(%s)" % (v, plugin_name))

    def common_methods_keys(self):
        return self.common_choices

    def common_address_keys(self):
        return self.address_choices

    def template_keys(self, payment_plugin_id=None, delivery_plugin_id=None):
        return itertools.chain(
            self.common_methods_keys(),
            self.common_address_keys(),
            self.payment_methods_keys(payment_plugin_id),
            self.delivery_methods_keys(delivery_plugin_id))
