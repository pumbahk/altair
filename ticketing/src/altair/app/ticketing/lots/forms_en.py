# -*- coding:utf-8 -*-
from datetime import datetime
from wtforms import fields
from wtforms import validators as v
from wtforms import Form
from wtforms import widgets

from altair.app.ticketing.cart.forms_en import ClientForm as _ClientForm
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
    'last_name': u"Last name",
    'first_name': u"First name",
    'zip': u"Zip",
    'tel_1': u"Tel 1",
    'sex': u"Sex",
    'email_1': u"Email 1",
    'email_1_confirm': u"Email 1 Confirmation",
    'email_2': u"Email 2",
    'city': u"City",
    'prefecture': u"Prefecture",
    'address_1': u"Address 1",
    'birthday': u"Birthday",
    }

class ClientForm(_ClientForm):
    sex = OurRadioField(u'Gender', choices=[(str(SexEnum.Male), u'Male'), (str(SexEnum.Female), u'Female')])
    birthday = OurDateField(
        u"Birthday",
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
    memo = fields.TextAreaField(u"Memo")

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

    entry_no = fields.TextField(u"Lottery application number", validators=[v.Required()])
    tel_no = fields.TextField(u"Telephone number", validators=[v.Required()])
