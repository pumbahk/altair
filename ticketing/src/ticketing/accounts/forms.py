# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField
from wtforms.validators import Required, Length, Optional

class AccountForm(Form):

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = TextField(
        label=u'クライアント名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
