# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import Account

class StockHolderForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.account_id.choices = [
                (account.id, account.name) for account in Account.get_by_organization_id(kwargs['organization_id'])
            ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()],
    )
    name = TextField(
        label=u'枠名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    account_id = SelectField(
        label=u'配券先',
        validators=[Required()],
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
