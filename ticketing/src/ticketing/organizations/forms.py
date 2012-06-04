# -*- coding: utf-8 -*-

import re

from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField, BooleanField
from wtforms.validators import Required, Length, Regexp, Optional

from ticketing.utils import DateTimeField, Translations
from ticketing.master.models import Prefecture

class Phone(Regexp):
    def __init__(self, message=None):
        super(Phone, self).__init__(r'^[0-9¥-]*$', re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'電話番号を確認してください')
        super(Phone, self).__call__(form, field)

class OrganizationForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = TextField(
        label=u'クライアント名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    client_type = SelectField(
        label=u'クライアントタイプ',
        choices=[(1, u'スタンダード')],
        coerce=int,
    )
    prefecture_id = SelectField(
        label=u'都道府県',
        validators=[
            Required(u'入力してください'),
        ],
        choices=[(pref.id, pref.name) for pref in Prefecture.all()],
        coerce=int,
    )
    city = TextField(
        label=u'市町村区',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    address = TextField(
        label=u'町名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    street = TextField(
        label=u'番地',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    other_address = TextField(
        label=u'アパート・マンション名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    tel_1 = TextField(
        label=u'電話番号',
        validators=[Phone()]
    )
    tel_2 = TextField(
        label=u'携帯電話番号',
        validators=[Phone()]
    )
    fax = TextField(
        label=u'FAX番号',
        validators=[Phone()]
    )

    '''
    company_name = TextField(
        label=u'会社名',
    )
    section_name = TextField(
        label=u'部署名'
    )
    zip_code = TextField(
        label=u'郵便番号'
    )
    country_code = SelectField(
        label=u'国',
        choices=[(81, u'日本')],
    )
    '''
