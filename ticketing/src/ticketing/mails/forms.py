# -*- coding:utf-8 -*-

import itertools
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators
from collections import namedtuple

def MethodChoicesFormFactory(template):
    attrs = {}
    choices = template.payment_methods_choices()
    attrs["payment_methods"] = fields.SelectField(label=u"決済方法", choices=choices, id="payment_methods")    
    choices = template.delivery_methods_choices()
    attrs["delivery_methods"] = fields.SelectField(label=u"配送方法", choices=choices, id="delivery_methods")
    return type("MethodChoiceForm", (Form, ), attrs)

def MailInfoFormFactory(template):
    attrs = {}
    for e in template.template_keys():
        attrs[e.name] = fields.TextField(label=e.label, widget=widgets.TextArea(), description=e.method, 
                                         validators=[validators.Optional()])

    choices = template.payment_methods_choices()
    attrs["payment_types"] = [e[0] for e in choices]

    choices = template.delivery_methods_choices()
    attrs["delivery_types"] = [e[0] for e in choices]

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

    payment_key_fmt = "P%d%s"
    delivery_key_fmt = "D%d%s"

    @classmethod
    def payment_key(self, order, k):
        self.payment_key_fmt % (order.payment_plugin_id, k)

    @classmethod
    def delivery_key(self, order, k):
        self.delivery_key_fmt % (order.delivery_plugin_id, k)


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
