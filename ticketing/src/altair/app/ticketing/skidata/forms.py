# -*- coding: utf-8 -*-

from altair.formhelpers.form import OurForm
from wtforms import TextField, IntegerField, HiddenField, SelectMultipleField, FileField
from wtforms.validators import Regexp, Length, Optional, ValidationError, StopValidation
from altair.formhelpers import DateTimeField, Translations, Required


class SkidataPropertyForm(OurForm):
    name = TextField(
        label=u'プロパティ名',
        validators=[
            Required(message=u'文字列を入力してください'),
            Length(max=30, message=u'30文字以内で入力してください'),
        ]
    )

    value = IntegerField(
        label=u'プロパティ値(数値)',
        validators=[Required(message=u'数値を入力してください')]
    )
