# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField, TextField, BooleanField
from wtforms.validators import Optional, Length

class TopForm(Form):

    # --- disp
    word = TextField(
        label = '',
        validators=[Length(max=200, message=u'200文字以内で入力してください')]
    )

    week_sale = BooleanField(
        label='',
        validators=[Optional()],
        default=False
    )

    soon_act = BooleanField(
        label='',
        validators=[Optional()],
        default=False
    )
    # ---

    genre = HiddenField(
        validators=[Optional()],
        default="0",
    )

    sub_genre = HiddenField(
        validators=[Optional()],
        default="0",
    )

    area = HiddenField(
        validators=[Optional()],
        default="0"
    )

    num = HiddenField(
        validators=[Optional()],
        default="0"
    )

    page = HiddenField(
        validators=[Optional()],
        default="0"
    )

    path = HiddenField(
        validators=[Optional()],
        default='/search'
    )

    topics = HiddenField(
        validators=[Optional()],
    )

    promotions = HiddenField(
        validators=[Optional()],
    )

    attentions = HiddenField(
        validators=[Optional()]
    )

    hotwords = HiddenField(
        validators=[Optional()],
    )

    genretree = HiddenField(
        validators=[Optional()],
    )
