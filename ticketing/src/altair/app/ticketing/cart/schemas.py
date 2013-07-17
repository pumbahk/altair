# -*- coding:utf-8 -*-

import re
import unicodedata
from wtforms import fields
from wtforms.form import Form
from wtforms.ext.csrf.session import SessionSecureForm
from wtforms.validators import Regexp, Length, NumberRange, EqualTo, Optional, ValidationError
from altair.formhelpers import OurForm, CP932
from altair.app.ticketing.core import models as c_models

from altair.formhelpers import (
    DateTimeField,
    Translations,
    Required,
    Phone,
    NFKC,
    Zenkaku,
    Katakana,
    SejCompliantEmail,
    Liaison,
    strip,
    strip_spaces,
    capitalize,
    ignore_regexp,
    ignore_space_hyphen
    )

class CSRFSecureForm(SessionSecureForm):
    SECRET_KEY = 'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'

class ClientForm(OurForm):
    def _get_translations(self):
        return Translations()

    last_name = fields.TextField(
        label=u"姓",
        filters=[strip_spaces],
        validators=[
            Required(),
            Zenkaku,
            Length(max=10, message=u'10文字以内で入力してください'),
        ],
    )
    last_name_kana = fields.TextField(
        label=u"姓(カナ)",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(),
            Katakana,
            Length(max=10, message=u'10文字以内で入力してください'),
        ]
    )
    first_name = fields.TextField(
        label=u"名",
        filters=[strip_spaces],
        validators=[
            Required(),
            Zenkaku,
            Length(max=10, message=u'10文字以内で入力してください'),
        ]
    )
    first_name_kana = fields.TextField(
        label=u"名(カナ)",
        filters=[strip_spaces, NFKC], 
        validators=[
            Required(),
            Katakana,
            Length(max=10, message=u'10文字以内で入力してください'),
        ]
    )
    tel_1 = fields.TextField(
        label=u"電話番号",
        filters=[ignore_space_hyphen], 
        validators=[
            Required(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください'), 
        ]
    )
    fax = fields.TextField(
        label=u"FAX番号",
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
            CP932,
        ]
    )
    city = fields.TextField(
        label=u"市区町村",
        filters=[strip_spaces],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
        ]
    )
    address_1 = fields.TextField(
        label=u"住所",
        filters=[strip_spaces],
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
        ]
    )
    address_2 = fields.TextField(
        label=u"住所 (建物名など)",
        filters=[strip_spaces],
        validators=[
            Length(max=255, message=u'255文字以内で入力してください'),
            CP932,
        ]
    )
    email_1 = fields.TextField(
        label=u"メールアドレス",
        filters=[strip_spaces],
        validators=[
            Required(),
            SejCompliantEmail(),
        ]
    )
    email_1_confirm = fields.TextField(
        label=u"メールアドレス (確認)",
        filters=[strip_spaces],
        validators=[
            Required(),
            SejCompliantEmail(),
        ]
    )
    # XXX: 黒魔術的。email_2 に値が入っていて email_1 に値が入っていなかったら、email_1 に値を移すという動作をする
    email_2 = Liaison(
        email_1,
        fields.TextField(
            label=u"メールアドレス",
            filters=[strip_spaces],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )
    # XXX: 黒魔術的。email_2_confirm に値が入っていて email_1_confirm に値が入っていなかったら、email_1 に値を移すという動作をする
    email_2_confirm = Liaison(
        email_1_confirm,
        fields.TextField(
            label=u"メールアドレス (確認)",
            filters=[strip_spaces],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )

    def _validate_email_addresses(self, *args, **kwargs):
        status = True
        data = self.data
        if data["email_1"] != data["email_1_confirm"]:
            getattr(self, "email_1").errors.append(u"メールアドレスと確認メールアドレスが一致していません。")
            status = False
        if data["email_2"] != data["email_2_confirm"]:
            getattr(self, "email_2").errors.append(u"メールアドレスと確認メールアドレスが一致していません。")
            status = False
        return status

    def validate(self):
        # このように and 演算子を展開しないとすべてが一度に評価されない
        status = super(ClientForm, self).validate()
        status = self._validate_email_addresses() and status
        return status
