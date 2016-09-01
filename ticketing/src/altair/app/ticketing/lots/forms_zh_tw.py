# -*- coding:utf-8 -*-
from datetime import datetime
from wtforms import fields
from wtforms import validators as v
from wtforms import Form
from wtforms import widgets

from altair.app.ticketing.cart.forms_zh_tw import ClientForm as _ClientForm
from altair.app.ticketing.cart.schemas import ExtraForm
from altair.app.ticketing.cart.view_support import build_dynamic_form, filter_extra_form_schema
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
from altair.formhelpers.fields.core import (
    OurSelectField,
    )
from wtforms.validators import AnyOf

ymd_widget = Switcher(
    'select',
    select=widgets.Select(),
    input=widgets.TextInput()
    )

client_form_fields = {
    'last_name': u"姓",
    'first_name': u"名",
    'zip': u"郵政編碼",
    'tel_1': u"電話號碼",
    'sex': u"性別",
    'email_1': u"電子郵件",
    'email_1_confirm': u"電子郵件(确认)",
    'email_2': u"電子郵件",
    'city': u"市",
    'prefecture': u"省",
    'address_1': u"地址",
    'birthday': u"出生日期",
    }

class ClientForm(_ClientForm):
    sex = OurRadioField(u'性別', choices=[(str(SexEnum.Male), u'男'), (str(SexEnum.Female), u'女')])
    birthday = OurDateField(
        u"生日",
        value_defaults={'year':u'1980'},
        missing_value_defaults={ 'year': u'', 'month': u'', 'day': u'', },
        widget=OurDateWidget(
            input_builder=build_date_input_select_japanese_japan
            ),
        validators=[
            Required(),
            after1900,
            ]
        )
    memo = fields.TextAreaField(u"備註")

    def get_validated_address_data(self):
        if self.validate():
            return dict(
                first_name=self.data['first_name'],
                last_name=self.data['last_name'],
                zip=self.data['zip'],
                prefecture=self.data['prefecture'],
                city=self.data['city'],
                address_1=self.data['address_1'],
                address_2=self.data['address_2'],
                country=self.data['country'],
                email_1=self.data['email_1'],
                tel_1=self.data['tel_1'],
                tel_2=self.data['tel_2'],
                fax=self.data['fax'],
                sex=self.data['sex']
                )

class ShowLotEntryForm(OurForm):
    def _get_translations(self):
        return Translations()

    entry_no = fields.TextField(u"抽選申請號碼", validators=[v.Required()])
    tel_no = fields.TextField(u"電話號碼", validators=[v.Required()])
