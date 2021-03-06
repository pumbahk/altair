# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, SelectField
from wtforms.validators import Required, Length, Optional

from altair.formhelpers.fields import LazySelectField
from altair.app.ticketing.master.models import Bank

class BankAccountForm(Form):

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    bank_id = LazySelectField(
        label=u'銀行種別',
        validators=[Required(u'選択してください')],
        choices=lambda field: [(bank.id, bank.name) for bank in Bank.all()],
        coerce=int
    )
    account_type = TextField(
        label=u'口座種別',
    )
    account_number = TextField(
        label=u'口座番号',
    )
    account_owner = TextField(
        label=u'口座名義',
    )
