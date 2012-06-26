# -*- coding:utf-8 -*-

from wtforms import fields
from wtforms.form import Form
from wtforms.validators import Regexp, Email, Length, NumberRange, EqualTo, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required, Phone


class CardForm(Form):

    card_number = fields.TextField(validators=[Length(16)])
    exp_year = fields.TextField(validators=[Length(2)])
    exp_month = fields.TextField(validators=[Length(2)])


class ClientForm(Form):

    def _get_translations(self):
        return Translations()

    last_name = fields.TextField(
        label=u"姓",
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    last_name_kana = fields.TextField(
        label=u"姓(カナ)",
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    first_name = fields.TextField(
        label=u"名",
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    first_name_kana = fields.TextField(
        label=u"名(カナ)",
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    tel = fields.TextField(
        label=u"TEL",
        validators=[
            Required(),
            Phone(),
        ]
    )
    fax = fields.TextField(
        label=u"FAX",
        validators=[
            Optional(),
            Phone(u'FAX番号を確認してください'),
        ]
    )
    zip = fields.TextField(
        label=u"郵便番号",
        validators=[
            Required(),
            Regexp(u'^[0-9¥-]*$', message=u'確認してください'),
            Length(max=8, message=u'確認してください'),
        ]
    )
    prefecture = fields.TextField(
        label=u"都道府県",
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    city = fields.TextField(
        label=u"市区町村",
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    address_1 = fields.TextField(
        label=u"住所",
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    address_2 = fields.TextField(
        label=u"住所",
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    mail_address = fields.TextField(
        label=u"メールアドレス",
        validators=[
            Required(),
            Email(),
        ]
    )
