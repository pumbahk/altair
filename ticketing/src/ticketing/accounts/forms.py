# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField
from wtforms.validators import Required, Length

class AccountForm(Form):
    name = TextField(
        label=u'クライアント名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
