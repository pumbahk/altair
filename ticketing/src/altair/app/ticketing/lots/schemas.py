# -*- coding:utf-8 -*-
from datetime import datetime
from wtforms import fields
from wtforms import validators as v
from wtforms import Form
from wtforms import widgets

from altair.app.ticketing.cart.schemas import ClientForm as _ClientForm, ExtraForm
from altair.app.ticketing.cart.view_support import build_dynamic_form
from altair.app.ticketing.users.models import SexEnum
from altair.formhelpers import (
    Required,
    text_type_but_none_if_not_given,
    Zenkaku,
    Katakana,
    NFKC,
    lstrip,
    strip,
    strip_hyphen,
    strip_spaces,
    SejCompliantEmail,
    CP932,
    Translations,
    )
from altair.formhelpers.widgets import (
    OurDateWidget,
    build_date_input_select_japanese_japan,
    )
from altair.formhelpers.fields import (
    OurDateField
    )
from altair.formhelpers.form import OurForm
from altair.formhelpers.widgets import Switcher
from altair.formhelpers.fields import OurRadioField
from altair.formhelpers.validators import (
    DateTimeFormat,
    after1900,
    )
from altair.formhelpers.fields import OurRadioField
from .fields import StringFieldWithChoice
from altair.now import get_now

ymd_widget = Switcher(
    'select',
    select=widgets.Select(),
    input=widgets.TextInput()
    )

class ClientForm(_ClientForm):
    sex = OurRadioField(u'性別', choices=[(str(SexEnum.Male), u'男性'), (str(SexEnum.Female), u'女性')])
    birthday = OurDateField(
        u"誕生日",
        value_defaults={ 'year': u'1980', },
        missing_value_defaults={ 'year': u'', 'month': u'', 'day': u'', },
        widget=OurDateWidget(
            input_builder=build_date_input_select_japanese_japan
            ),
        validators=[
            Required(),
            after1900,
            ]
        )
    memo = fields.TextAreaField(u"メモ")

    def get_validated_address_data(self):
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
                email_1=self.data['email_1'],
                tel_1=self.data['tel_1'],
                tel_2=self.data['tel_2'],
                fax=self.data['fax'],
                sex=self.data['sex']
                )

class DynamicExtraForm(ExtraForm):
    def __init__(self, *args, **kwargs):
        context = kwargs.get('context')
        fields = build_dynamic_form.unbound_fields(context.cart_setting.extra_form_fields or [])
        super(DynamicExtraForm, self).__init__(*args, _fields=fields, **kwargs)


class ShowLotEntryForm(OurForm):
    def _get_translations(self):
        return Translations()

    entry_no = fields.TextField(u"抽選申し込み番号", validators=[v.Required()])
    tel_no = fields.TextField(u"電話番号", validators=[v.Required()])
