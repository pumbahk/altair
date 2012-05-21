# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms.validators import Required, Regexp, Length, Optional, ValidationError

from ticketing.utils import DateTimeField
from ticketing.venues.models import Venue
from ticketing.events.models import Account

class StockHolderForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.account_id.choices = [
                (account.id, account.name) for account in Account.get_by_organization_id(kwargs['organization_id'])
            ]

    id = HiddenField(
        label='',
        validators=[Optional()],
    )
    performance_id = HiddenField(
        label='',
        validators=[Required()],
    )
    name = TextField(
        label=u'枠名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    account_id = SelectField(
        label=u'配券先',
        validators=[Required(u'入力してください')],
        choices=[],
        coerce=int
    )
    text = TextField(
        label=u'記号',
        validators=[Required()]
    )
    text_color = TextField(
        label=u'記号色',
        validators=[Required()]
    )
