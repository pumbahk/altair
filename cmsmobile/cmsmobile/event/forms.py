# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, BooleanField
from wtforms.validators import Length
from wtforms.validators import Optional, ValidationError

class SearchForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

    genre = HiddenField(
        label='',
        validators=[Optional()],
        default="",
    )

    sub_genre = HiddenField(
        label='',
        validators=[Optional()],
        default="",
    )

    area = HiddenField(
        label='',
        validators=[Optional()],
        default="",
    )

    num = HiddenField(#総件数
        label='',
        validators=[Optional()],
        default="0"
    )

    page = HiddenField(#現在ページ
        label='',
        validators=[Optional()],
        default='1',
    )

    page_num = HiddenField(#総ページ数
        label='',
        validators=[Optional()],
        default="0"
    )

    path = HiddenField(
        label='',
        validators=[Optional()],
        default='/search'
    )

    word = TextField(
        label = '',
        validators=[
            Length(max=200, message=u'200文字以内で入力してください'),
            ]
    )

    week_sale = BooleanField(
        label = '',
        validators=[Optional()],
        default=False
    )

    soon_sale = BooleanField(
        label = '',
        validators=[Optional()],
        default=False
    )

class HotwordForm(Form):
    id = HiddenField(
        label='',
        validators=[Optional()],
        default="",
    )
