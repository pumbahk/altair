# -*- coding:utf-8 -*-

from wtforms import fields
from wtforms.form import Form
from wtforms.ext.csrf.session import SessionSecureForm
from wtforms.validators import Regexp, Email, Length, NumberRange, EqualTo, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required, Phone

CARD_NUMBER_REGEXP = r'^\d{15,16}$'
CARD_HOLDER_NAME_REGEXP = r'^[A-Z\s]+$'
CARD_EXP_YEAR_REGEXP = r'^\d{2}$'
CARD_EXP_MONTH_REGEXP = r'^\d{2}$'
CARD_SECURE_CODE_REGEXP = r'^\d{3,4}$'

def capitalize(unistr):
    return unistr and unistr.upper()

class CardForm(SessionSecureForm):
    SECRET_KEY = 'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'
    def _get_translations(self):
        return Translations({
            'This field is required.' : u'入力してください',
            'Not a valid choice' : u'選択してください',
            'Invalid email address.' : u'Emailの形式が正しくありません。',
            'Field must be at least %(min)d characters long.' : u'正しく入力してください。',
            'Field must be between %(min)d and %(max)d characters long.': u'正しく入力してください。',
            'Invalid input.': u'形式が正しくありません。',
        })

    card_number = fields.TextField('card', validators=[Length(15, 16), Regexp(CARD_NUMBER_REGEXP), Required()])
    exp_year = fields.TextField('exp_year', validators=[Length(2), Regexp(CARD_EXP_YEAR_REGEXP)])
    exp_month = fields.TextField('exp_month', validators=[Length(2), Regexp(CARD_EXP_MONTH_REGEXP)])
    card_holder_name = fields.TextField('card_holder_name', filters=[capitalize], validators=[Length(2), Regexp(CARD_HOLDER_NAME_REGEXP)])
    secure_code = fields.TextField('secure_code', validators=[Length(3, 4), Regexp(CARD_SECURE_CODE_REGEXP)])

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
