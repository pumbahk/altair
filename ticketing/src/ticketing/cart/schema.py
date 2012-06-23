# -*- coding:utf-8 -*-

from wtforms import fields, validators
from wtforms.form import Form


class CardForm(Form):
    card_number = fields.TextField(validators=[validators.length(16)])
    exp_year = fields.TextField(validators=[validators.length(2)])
    exp_month = fields.TextField(validators=[validators.length(2)])

class ClientForm(Form):
    last_name = fields.TextField(u"姓", validators=[validators.required()])
    last_name_kana = fields.TextField(u"姓(カナ)", validators=[validators.required()])
    first_name = fields.TextField(u"名", validators=[validators.required()])
    first_name_kana = fields.TextField(u"名(カナ)", validators=[validators.required()])
    tel_1 = fields.TextField(u"TEL", validators=[validators.required()])
    fax = fields.TextField(u"FAX")
    zip = fields.TextField(u"郵便番号", validators=[validators.required()])
    prefecture = fields.TextField(u"都道府県", validators=[validators.required()])
    city = fields.TextField(u"市区町村", validators=[validators.required()])
    address_1 = fields.TextField(u"住所2", validators=[validators.required()])
    address_2 = fields.TextField(u"住所1", validators=[])

    mail_address = fields.TextField(u"メールアドレス", validators=[validators.required()])
