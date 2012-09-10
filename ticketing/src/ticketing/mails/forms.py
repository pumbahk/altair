# -*- coding:utf-8 -*-

import itertools
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from collections import namedtuple, OrderedDict
from ticketing.cart import helpers as ch

def MethodChoicesFormFactory(template):
    attrs = {}
    choices = [(m.payment_plugin_id, m.name)
               for m in template.organization.payment_method_list]
    attrs["payment_methods"] = fields.SelectField(label=u"決済方法", choices=choices, id="payment_methods")    

    choices = [(m.delivery_plugin_id, m.name)
               for m in template.organization.delivery_method_list]
    attrs["delivery_methods"] = fields.SelectField(label=u"配送方法", choices=choices, id="delivery_methods")
    return type("MethodChoiceForm", (Form, ), attrs)

OrderInfo = namedtuple("OrderInfo", "name label getval")
RenderVal = namedtuple("RenderVal", "status label, body")
class OrderInfoForm(Form):
    use = fields.BooleanField(u"表示する")
    kana = fields.TextField(u"ラベル名", validators=[validators.Required()])

class OrderInfoDefault(object):
    """ 
    以下の情報のデフォルトの値。ラベル名が変えられ、表示するかしないか選択できる。
    #注文情報 受付番号、受付日時、公演タイトル、商品名、座席番号、商品代金、サービス利用料・手数料、合計金額
    """
    def get_event_title(order):
        performance = order.performance
        return u"{0} {1}".format(performance.event.title, performance.name)

    def get_performance_date(order):
        return ch.japanese_datetime(order.performance.start_on)

    def get_seat_no(order):
        seats = itertools.chain.from_iterable((p.seats for p in order.ordered_products))
        return u"\n".join(u"* {0}".format(seat["name"]) for seat in seats)

    def get_product_description(order):
        return u"\n".join((u"{0} {1} x{2}枚".format(op.product.name, 
                                                    ch.format_currency(op.product.price),
                                                    op.quantity)
                           for op in order.ordered_products))

    def get_name_kana(order):
        sa = order.shipping_address
        return u"{0} {1}".format(sa.last_name_kana, sa.first_name_kana),

    name_kana = OrderInfo(name="name_kana", label=u"お名前カナ", getval=get_name_kana)
    tel = OrderInfo(name="tel", label=u"電話番号", getval=lambda order : order.shipping_address.tel_1 or "")
    mail = OrderInfo(name="mail", label=u"メールアドレス", getval=lambda order : order.shipping_address.email)
    order_no = OrderInfo(name="order_no", label=u"受付番号", getval=lambda order : order.order_no)
    order_datetime = OrderInfo(name="order_datetime", label=u"受付日", getval=lambda order: ch.mail_date(order.created_at))
    event_name = OrderInfo(name="event_name", label=u"公演タイトル", getval=get_event_title)
    pdate = OrderInfo(name="pdate", label=u"公演日時", getval=get_performance_date)
    venue = OrderInfo(name="venue", label=u"会場", getval=lambda order: order.performance.venue.name)
    for_product =OrderInfo(name="for_product", label=u"商品代金", getval=get_product_description)
    for_seat = OrderInfo(name=u"for_seat", label=u"ご購入いただいた座席", getval=get_seat_no)
    system_fee = OrderInfo(name=u"system_fee", label=u"システム利用料", getval=lambda order: ch.format_currency(order.system_fee))
    transaction_fee = OrderInfo(name=u"transaction_fee", label=u"決済手数料", getval=lambda order: ch.format_currency(order.transaction_fee))
    delivery_fee = OrderInfo(name=u"delivery_fee", label=u"発券／配送手数料", getval=lambda order: ch.format_currency(order.delivery_fee))
    total_amount = OrderInfo(name=u"total_amount", label=u"合計金額", getval=lambda order: ch.format_currency(order.total_amount))

    @classmethod
    def get_form_field_candidates(cls):
        return ((k,v) for k,v in cls.__dict__.iteritems() if isinstance(v, OrderInfo))

class OrderInfoRenderer(object):
    default = OrderInfoDefault
    def __init__(self, order, data):
        self.order = order
        self.data = data

    def get(self, k):
        if not hasattr(self, k):
            val = self.data[k]
            if not (val and val["use"]):
                setattr(self, k, RenderVal(label="", status=False, body=""))
            else:
                setattr(self, k, RenderVal(label=val["kana"],
                                           status=True, 
                                           body=getattr(self.default, k).getval(self.order)))
        return getattr(self, k)

def MailInfoFormFactory(template):
    attrs = OrderedDict()
    attrs["subject"] = fields.TextField(label=u"メール件名")
    attrs["sender"] = fields.TextField(label=u"メールsender")

    for k, v in OrderInfoDefault.get_form_field_candidates():
        attrs[k] = fields.FormField(OrderInfoForm, label=v.label, default=dict(use=True, kana=v.label, doc=v)) ##xxx:

    for e in template.template_keys():
        attrs[e.name] = fields.TextField(label=e.label, widget=widgets.TextArea(), description=e.method, 
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
        return status
    attrs["validate"] = validate

    def as_mailinfo_data(self):
        return {k:v for k, v in self.data.iteritems() if v}
    attrs["as_mailinfo_data"] = as_mailinfo_data

    return type("MailInfoForm", (Form, ), attrs)

PluginInfo = namedtuple("PluginInfo", "method name label") #P0, P0notice, 注意事項(コンビに決済)    
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
        return MailInfoFormFactory(self)

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

    def __init__(self, request, organization):
        self.request = request
        self.organization = organization

    payment_key_fmt = "P%s%s"
    delivery_key_fmt = "D%s%s"

    @classmethod
    def payment_key(self, order, k):
        payment_plugin_id  = order.payment_delivery_pair.payment_method.payment_plugin_id
        return self.payment_key_fmt % (payment_plugin_id, k)

    @classmethod
    def delivery_key(self, order, k):
        delivery_plugin_id  = order.payment_delivery_pair.delivery_method.delivery_plugin_id
        return self.delivery_key_fmt % (delivery_plugin_id, k)


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

    def template_keys(self, payment_plugin_id=None, delivery_plugin_id=None):
        return itertools.chain(
            self.common_methods_keys(), 
            self.payment_methods_keys(payment_plugin_id), 
            self.delivery_methods_keys(delivery_plugin_id))
