# -*- coding:utf-8 -*-

import re
import unicodedata
from wtforms import fields
from wtforms.form import Form
from wtforms.validators import Regexp, Length, NumberRange, EqualTo, Optional, ValidationError
from ticketing.validators import Email
from ticketing.core import models as c_models

from ticketing.formhelpers import (
    DateTimeField,
    Translations,
    Required,
    Phone,
    NFKC,
    Zenkaku,
    Katakana,
    SejCompliantEmail,
    strip,
    strip_spaces,
    capitalize,
    ignore_regexp,
    ignore_space_hyphen
    )


class ClientForm(Form):

    def get_validated_address_data(self):
        """フォームから ShippingAddress などの値を取りたいときはこれで"""
        if self.validate():
            return dict(
                first_name=self.data['first_name'],
                last_name=self.data['last_name'],
                first_name_kana=self.data['first_name_kana'],
                last_name_kana=self.data['last_name_kana'],
                zip=self.data['zip'],
                prefecture=self.data['prefecture'],
                city=self.data['city'],
                address_1=self.data['address_1'],
                address_2=self.data['address_2'],
                country=u"日本国",
                email=self.data['mail_address'],
                tel_1=self.data['tel'],
                tel_2=self.data.get('mobile_tel'),
                fax=self.data['fax']
                )
        else:
            return None

    def create_shipping_address(self, user, data):
        return c_models.ShippingAddress(
            first_name=data['first_name'],
            last_name=data['last_name'],
            first_name_kana=data['first_name_kana'],
            last_name_kana=data['last_name_kana'],
            zip=data['zip'],
            prefecture=data['prefecture'],
            city=data['city'],
            address_1=data['address_1'],
            address_2=data['address_2'],
            country=data['country'],
            email=data['email'],
            tel_1=data['tel_1'],
            tel_2=data['tel_2'],
            fax=data['fax'],
            sex=data.get('sex'),
            user=user
        )


    def _get_translations(self):
        return Translations()

    last_name = fields.TextField(
        label=u"姓",
        filters=[strip_spaces],
        validators=[
            Required(),
            Zenkaku, 
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    last_name_kana = fields.TextField(
        label=u"姓(カナ)",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(),
            Katakana, 
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    first_name = fields.TextField(
        label=u"名",
        filters=[strip_spaces],
        validators=[
            Required(),
            Zenkaku, 
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    first_name_kana = fields.TextField(
        label=u"名(カナ)",
        filters=[strip_spaces, NFKC], 
        validators=[
            Required(),
            Katakana, 
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    tel = fields.TextField(
        label=u"TEL",
        filters=[ignore_space_hyphen], 
        validators=[
            Required(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください'), 
        ]
    )
    fax = fields.TextField(
        label=u"FAX",
        filters=[ignore_space_hyphen], 
        validators=[
            Optional(),
            Length(min=1, max=11),
            Phone(u'FAX番号を確認してください'),
        ]
    )
    zip = fields.TextField(
        label=u"郵便番号",
        filters=[ignore_space_hyphen], 
        validators=[
            Required(),
            Regexp(r'^\d{7}$', message=u'-を抜いた数字(7桁)のみを入力してください'), 
            Length(min=7, max=7, message=u'確認してください'),
        ]
    )
    prefecture = fields.TextField(
        label=u"都道府県",
        filters=[strip_spaces],
        ## 89ersではSelectFieldになっている
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    city = fields.TextField(
        label=u"市区町村",
        filters=[strip_spaces],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    address_1 = fields.TextField(
        label=u"住所",
        filters=[strip_spaces],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    address_2 = fields.TextField(
        label=u"住所",
        filters=[strip_spaces],
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    mail_address = fields.TextField(
        label=u"メールアドレス",
        filters=[strip_spaces],
        validators=[
            Required(),
            SejCompliantEmail(),
        ]
    )
    mail_address2 = fields.TextField(
        label=u"確認用メールアドレス",
        filters=[strip_spaces],
        validators=[
            Required(),
            SejCompliantEmail(),
        ]
    )

    def validate(self):
        status = super(ClientForm, self).validate()

        data = self.data
        if data["mail_address"] != data["mail_address2"]:
            getattr(self, "mail_address").errors.append(u"メールアドレスと確認メールアドレスが一致していません。")
            status = False
        return status
