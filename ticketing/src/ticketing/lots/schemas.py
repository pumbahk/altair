# -*- coding:utf-8 -*-

from wtforms import fields
from wtforms import validators as v
from wtforms import Form
from ticketing.cart.schemas import ClientForm as _ClientForm



class ClientForm(_ClientForm):
    sex = fields.TextField(u'性別')
    mobile_tel = fields.TextField(u'電話番号(携帯)')

class ShowLotEntryForm(Form):
    entry_no = fields.TextField(u"抽選申し込み番号", validators=[v.Required()])
    tel_no = fields.TextField(u"電話番号", validators=[v.Required()])
