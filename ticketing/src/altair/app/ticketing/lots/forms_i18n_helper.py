# -*- coding:utf-8 -*-
from altair.app.ticketing.cart.forms_i18n_helper import *
from altair.app.ticketing.i18n import custom_locale_negotiator
client_form_fields = {
    'last_name': u"姓",
    'first_name': u"名",
    'zip': u"郵便番号",
    'tel_1': u"電話番号",
    'sex': u"性別",
    'email_1': u"メールアドレス",
    'email_1_confirm': u"メールアドレス（確認）",
    'email_2': u"メールアドレス",
    'city': u"市区町村",
    'prefecture': u"都道府県を",
    'address_1': u"住所",
    'birthday': u"生年月日",
    }

client_form_fields_jp = {
    'last_name_kana' : u"姓（カナ）",
    'first_name_kana': u"名（カナ）",
    }

def get_client_form_fields(request):
    locale_name = custom_locale_negotiator(request)
    _ = request.translate
    if locale_name == 'ja':
        client_form_fields.update(client_form_fields_jp)
    return {key:_(client_form_fields.get(key)) for key in client_form_fields}



