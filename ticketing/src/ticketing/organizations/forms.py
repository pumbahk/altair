# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField, BooleanField
from wtforms.validators import Required, Length, Optional

from ticketing.master.models import Prefecture

class OrganizationForm(Form):

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
    )
    prefecture_id = SelectField(
        label=u'都道府県',
        choices=[(pref.id, pref.name) for pref in Prefecture.all()],
    )
    city = TextField(
        label=u'市町村区',
    )
    address = TextField(
        label=u'町名',
    )
    street = TextField(
        label=u'番地',
    )
    other_address = TextField(
        label=u'アパート・マンション名',
    )
    tel_1 = TextField(
        label=u'電話番号',
    )
    tel_2 = TextField(
        label=u'携帯電話番号',
    )
    fax = TextField(
        label=u'FAX番号',
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
