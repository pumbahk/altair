# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField, BooleanField
from wtforms.validators import Length, Regexp, Email, Optional

from ticketing.formhelpers import DateTimeField, Translations, Required, Phone
from ticketing.master.models import Prefecture

class OrganizationForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = TextField(
        label=u'取引先名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    code = TextField(
        label = u'企業コード',
        validators=[
            Required(),
            Regexp(u'^[A-Z0-9]*$', message=u'数字およびアルファベット大文字のみ入力できます'),
            Length(min=2, max=2, message=u'2文字で入力してください'),
        ]
    )
    client_type = SelectField(
        label=u'取引先タイプ',
        choices=[(1, u'スタンダード')],
        coerce=int,
    )
    contact_email = TextField(
        label = u'問い合わせメールアドレス',
        validators=[
            Required(),
            Email(),
        ]
    )
    prefecture_id = SelectField(
        label=u'都道府県',
        validators=[
            Required(u'入力してください'),
        ],
        choices=[(pref.name, pref.name) for pref in Prefecture.all()]
    )
    city = TextField(
        label=u'市町村区',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    address = TextField(
        label=u'町名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    street = TextField(
        label=u'番地',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    other_address = TextField(
        label=u'アパート・マンション名',
        validators=[
            Required(),
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

class SejTenantForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.organization_id.data = kwargs['organization_id']

    def _get_translations(self):
        return Translations()

    organization_id = HiddenField(
        label='',
        validators=[Optional()],
    )
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    shop_id = TextField(
        label=u'ショップID',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    shop_name = TextField(
        label=u'ショップ名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    contact_01 = TextField(
        label=u'連絡先1',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    contact_02 = TextField(
        label=u'連絡先2',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    api_key = TextField(
        label=u'API KEY',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    inticket_api_url = TextField(
        label=u'API URL',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
