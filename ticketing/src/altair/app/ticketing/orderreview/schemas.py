# -*- coding:utf-8 -*-
from wtforms import Form
from wtforms import fields
from wtforms import widgets
from wtforms import validators as v
from wtforms.ext.i18n.utils import DefaultTranslations
from wtforms.ext.csrf.fields import CSRFTokenField
from wtforms import ValidationError

from altair.formhelpers import SejCompliantEmail
from altair.formhelpers.form import OurDynamicForm, SecureFormMixin
from altair.formhelpers.fields import OurTextField
from altair.app.ticketing.master.models import Prefecture
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.cart.view_support import DynamicFormBuilder
from datetime import date, datetime
import unicodedata
from altair.formhelpers import Translations

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
def strip_hyphen(unistr):
    return unistr and REGEX_HYPHEN.sub('', unistr)

strip_spaces = strip(u' 　')

def remove_all_spaces(value):
    return value.replace(' ', '') if value else ''

class JForm(Form):
    def _get_translations(self):
        return Translations({
            'Field must be at least %(min)d characters long.' : u'正しく入力してください。',
            'Field must be between %(min)d and %(max)d characters long.': u'正しく入力してください。',
            })


class SendMailSchema(JForm):
    mail = fields.TextField(u"送り先メールアドレス", validators=[v.Required(), SejCompliantEmail(u'Emailの形式が正しくありません。')])


class QRTicketSendMailSchema(JForm):
    email = fields.TextField(u"送り先メールアドレス",
                             validators=[v.Required(u'Emailを入力してください'),
                                         SejCompliantEmail(u'Emailの形式が正しくありません')])


class OrderReviewSchema(JForm):
    order_no = fields.TextField(u"注文番号", filters=[strip_spaces], validators=[v.Required(u'入力してください')])
    tel = fields.TextField(u"電話番号", filters=[strip_spaces, strip_hyphen], validators=[v.Required(u'入力してください')])


class ReviewPasswordSchema(JForm):
    review_password = OurTextField(
        label=u'受付番号確認用パスワード',
        validators=[
            v.Required(message=u'入力してください'),
            v.Regexp(r'^(?=.*[a-zA-Z])(?=.*[0-9])([A-Za-z0-9]+)$', 0, message=u'正しく入力してください')
        ]
    )
    email = OurTextField(
        label=u'メールアドレス',
        filters=[NFKC, remove_all_spaces],
        validators=[
            v.Required(message=u'入力してください'),
            SejCompliantEmail(u'Emailの形式が正しくありません。')
        ]
    )
    type = OurTextField(
        label=u'区分コード',
    )


class OrderReviewOrderAttributeForm(OurDynamicForm, SecureFormMixin):
    SECRET_KEY = __name__
    csrf = CSRFTokenField()

    def __init__(self, **kwargs):
        self._dynswitch_predefined_symbols = kwargs.pop('_dynswitch_predefined_symbols', {})
        super(OrderReviewOrderAttributeForm, self).__init__(name_builder=DynamicFormBuilder._name_builder, **kwargs)

build_dynamic_form = DynamicFormBuilder(form_factory=OrderReviewOrderAttributeForm)


class PassportUserImageUploadForm(Form):
    passport_user_id = fields.HiddenField(u"PassportUserID")
    order_no = fields.HiddenField(u"予約番号")
    tel = fields.HiddenField(u"電話番号")
    upload_file = fields.FileField(label=u"imageファイル")

    def validate_upload_file(form, field):
        if not hasattr(field.data, "filename"):
            raise ValidationError(u"ファイルを指定してください")
        if not (field.data.filename.endswith('.png') or field.data.filename.endswith('.jpg')):
            raise ValidationError(u"jpg/pngファイルのみアップロード可能です。")


class PassportUserImageConfirmForm(Form):
    order_no = fields.HiddenField(u"予約番号")
    confirm = fields.HiddenField(label=u"確定")
