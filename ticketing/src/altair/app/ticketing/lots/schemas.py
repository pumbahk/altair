# -*- coding:utf-8 -*-
from datetime import datetime
from wtforms import fields
from wtforms import validators as v
from wtforms import Form
from wtforms import widgets

from altair.app.ticketing.cart.schemas import ClientForm as _ClientForm
from altair.app.ticketing.users.models import SexEnum
from altair.app.ticketing.booster import widgets as my_widgets
from altair.app.ticketing.booster import fields as my_fields
from altair.formhelpers import text_type_but_none_if_not_given, Zenkaku, Katakana, NFKC, lstrip, strip, strip_hyphen, strip_spaces, SejCompliantEmail, CP932, Translations
from altair.formhelpers.form import OurForm 
from altair.formhelpers.fields import OurRadioField

ymd_widget = my_widgets.Switcher(
    'select',
    select=widgets.Select(),
    input=widgets.TextInput()
    )

def get_year_choices():
    current_year = datetime.now().year
    years =  [(str(year), year) for year in range(current_year-100, current_year)]
    return years

def get_year_months():
    months =  [(str(month), month) for month in range(1,13)]
    return months

def get_year_days():
    days =  [(str(month), month) for month in range(1,32)]
    return days


class ClientForm(_ClientForm):
    sex = OurRadioField(u'性別', choices=[(str(SexEnum.Male), u'男性'), (str(SexEnum.Female), u'女性')])
    tel_2 = fields.TextField(u'電話番号(携帯)')
    year = my_fields.StringFieldWithChoice(u"年", filters=[strip_spaces], choices=get_year_choices(), default=str(datetime.now().year - 25), widget=ymd_widget)
    month = my_fields.StringFieldWithChoice(u"月", filters=[strip_spaces, lstrip('0')], validators=[v.Required()], choices=get_year_months(), widget=ymd_widget)
    day = my_fields.StringFieldWithChoice(u"日", filters=[strip_spaces, lstrip('0')], validators=[v.Required()], choices=get_year_days(), widget=ymd_widget)
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

class ShowLotEntryForm(OurForm):
    def _get_translations(self):
        return Translations()

    entry_no = fields.TextField(u"抽選申し込み番号", validators=[v.Required()])
    tel_no = fields.TextField(u"電話番号", validators=[v.Required()])
