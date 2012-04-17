 # -*- coding: utf-8 -*-
from ticketing.master.models import Prefecture, BankAccount

from wtforms import TextField, PasswordField, TextAreaField, DateField, SelectField, SubmitField, HiddenField, BooleanField, FileField
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms import Form

class TicketerForm(Form):
    name  = TextField(u'名前', validators=[Required()])
    zip   = TextField(u'郵便番号', validators=[])

    prefecture_id = SelectField(u'都道府県', choices=Prefecture.all_tuple(), validators=[Required()])

    city            = TextField(u'市町村', validators=[Required()])
    address         = TextField(u'住所１', validators=[Required()])
    street          = TextField(u'住所２', validators=[Required()])
    other_address   = TextField(u'住所３', validators=[Required()])
    tel_1           = TextField(u'電話番号１', validators=[Required()])
    tel_2           = TextField(u'郵便番号２', validators=[Required()])
    fax             = TextField(u'Fax', validators=[Required()])

