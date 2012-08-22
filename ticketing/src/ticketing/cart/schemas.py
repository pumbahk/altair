# -*- coding:utf-8 -*-

import unicodedata
from wtforms import fields
from wtforms.form import Form
from wtforms.ext.csrf.session import SessionSecureForm
from wtforms.validators import Regexp, Email, Length, NumberRange, EqualTo, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required, Phone

CARD_NUMBER_REGEXP = r'^\d{14,16}$'
CARD_HOLDER_NAME_REGEXP = r'^[A-Z\s]+$'
CARD_EXP_YEAR_REGEXP = r'^\d{2}$'
CARD_EXP_MONTH_REGEXP = r'^\d{2}$'
CARD_SECURE_CODE_REGEXP = r'^\d{3,4}$'

Zenkaku = Regexp(r"^[^\x01-\x7f]+$", message=u'全角で入力してください')
Katakana = Regexp(ur'^[ァ-ヶ]+$', message=u'カタカナで入力してください')

def capitalize(unistr):
    return unistr and unistr.upper()

def strip(chars):
    def stripper(unistr):
        return unistr and unistr.strip(chars)
    return stripper
strip_spaces = strip(u' 　')

def NFKC(unistr):
    return unistr and unicodedata.normalize('NFKC', unistr)

class CSRFSecureForm(SessionSecureForm):
    SECRET_KEY = 'EPj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Ym'


class CardForm(CSRFSecureForm):
    def _get_translations(self):
        return Translations({
            'This field is required.' : u'入力してください',
            'Not a valid choice' : u'選択してください',
            'Invalid email address.' : u'Emailの形式が正しくありません。',
            'Field must be at least %(min)d characters long.' : u'正しく入力してください。',
            'Field must be between %(min)d and %(max)d characters long.': u'正しく入力してください。',
            'Invalid input.': u'形式が正しくありません。',
        })

    card_number = fields.TextField('card', validators=[Length(14, 16), Regexp(CARD_NUMBER_REGEXP), Required()])
    exp_year = fields.TextField('exp_year', validators=[Length(2), Regexp(CARD_EXP_YEAR_REGEXP)])
    exp_month = fields.TextField('exp_month', validators=[Length(2), Regexp(CARD_EXP_MONTH_REGEXP)])
    card_holder_name = fields.TextField('card_holder_name', filters=[capitalize], validators=[Length(2), Regexp(CARD_HOLDER_NAME_REGEXP)])
    secure_code = fields.TextField('secure_code', validators=[Length(3, 4), Regexp(CARD_SECURE_CODE_REGEXP)])

class ClientForm(Form):

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
        filters=[strip_spaces],
        validators=[
            Required(),
            Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください'), 
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
        filters=[strip_spaces],
        validators=[
            Required(),
            Regexp(r'^\d*$', message=u'-を抜いた数字のみを入力してください'), 
            Length(max=8, message=u'確認してください'),
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
            Email(),
        ]
    )
