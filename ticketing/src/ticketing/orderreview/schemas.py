# -*- coding:utf-8 -*-
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators as v
from wtforms.ext.i18n.utils import DefaultTranslations
from wtforms import ValidationError

from ticketing.master.models import Prefecture
from ticketing.core import models as c_models
from datetime import date, datetime
import unicodedata
from ticketing.formhelpers import Translations

from . import fields as my_fields
from . import widgets as my_widgets

import re

ymd_widget = my_widgets.Switcher(
    'select',
    select=widgets.Select(),
    input=widgets.TextInput()
    )

radio_list_widget = my_widgets.Switcher(
    'list',
    list=widgets.ListWidget(prefix_label=False),
    plain=my_widgets.GenericSerializerWidget(prefix_label=False)
    )

def text_type_but_none_if_not_given(value):
    return unicode(value) if value is not None else None

def get_year_choices():
    current_year = datetime.now().year
    years =  [(str(year), year) for year in range(current_year-100, current_year)]
    return years

def get_year_months():
    months =  [(str(month), month) for month in range(1,13)]
    return months

def get_year_days():
    days =  [(str(month), month) for month in range(1,32)]
    return days

Zenkaku = v.Regexp(r"^[^\x01-\x7f]+$", message=u'全角で入力してください')
Katakana = v.Regexp(ur'^[ァ-ヶ]+$', message=u'カタカナで入力してください')

def NFKC(unistr):
    return unistr and unicodedata.normalize('NFKC', unistr)

def lstrip(chars):
    def stripper(unistr):
        return unistr and unistr.lstrip(chars)
    return stripper

def strip(chars):
    def stripper(unistr):
        return unistr and unistr.strip(chars)
    return stripper

REGEX_HYPHEN = re.compile('\-')
def strip_hyphen():
    def stripper(unistr):
        return unistr and REGEX_HYPHEN.sub('', unistr)
    return stripper

strip_spaces = strip(u' 　')

class OrderReviewSchema(Form):
    def _get_translations(self):
        return Translations({
            'This field is required.' : u'入力してください',
            'Not a valid choice' : u'選択してください',
            'Invalid email address.' : u'Emailの形式が正しくありません。',
            'Field must be at least %(min)d characters long.' : u'正しく入力してください。',
            'Field must be between %(min)d and %(max)d characters long.': u'正しく入力してください。',
            'Invalid input.': u'形式が正しくありません。',
        })

    order_no = fields.TextField(u"注文番号", filters=[strip_spaces], validators=[v.Required()])
    tel = fields.TextField(u"電話番号", filters=[strip_spaces, strip_hyphen()], validators=[v.Required()])

    def object_validate(self, order):
        if order is None or order.shipping_address is None:
            self.errors["order_no"] = [u'受付番号または電話番号が違います。']
            return False
        address = order.shipping_address
        if address.tel_1 != self.data["tel"] and address.tel_2 != self.data["tel"] :
            self.errors["order_no"] = [u'受付番号または電話番号が違います。']
            return False
        return True
