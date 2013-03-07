# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, BooleanField
from wtforms.validators import Length
from wtforms.validators import Optional

class EventDetailForm(Form):

    event_id = HiddenField(
        label='',
        validators=[Optional()],
        default="0",
    )

    event = HiddenField(
        label='',
        validators=[Optional()],
    )

    week = HiddenField(
        label='',
        validators=[Optional()],
    )
