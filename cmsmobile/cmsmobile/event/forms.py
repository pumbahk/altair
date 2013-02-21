# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField
from wtforms.validators import Length
from wtforms.validators import ValidationError

class SearchForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

    word = TextField(
        label = u'検索文字列',
        validators=[
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )

    def validate_word(form, field):
        if field.data == "":
            raise ValidationError(u'検索文字列を入れてください。')
