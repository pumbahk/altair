# -*- coding:utf-8 -*-

from wtforms import fields
from wtforms import validators as v
from wtforms import Form
from ticketing.cart.schemas import ClientForm as _ClientForm
from ticketing.users.models import SexEnum


class ClientForm(_ClientForm):
    sex = fields.RadioField(u'性別', choices=[(str(SexEnum.Male), u'男性'), (str(SexEnum.Female), u'女性')])
    tel_2 = fields.TextField(u'電話番号(携帯)')

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

class ShowLotEntryForm(Form):
    entry_no = fields.TextField(u"抽選申し込み番号", validators=[v.Required()])
    tel_no = fields.TextField(u"電話番号", validators=[v.Required()])
