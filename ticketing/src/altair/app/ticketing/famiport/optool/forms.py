# -*- coding: utf-8 -*-

from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, DateTimeField
from altair.formhelpers.widgets import OurPasswordInput, OurTextInput, OurDateWidget
from altair.formhelpers import Max, after1900
from wtforms.validators import Required, Length, Optional

class LoginForm(OurForm):
    user_name = OurTextField(
        validators=[
            Required(),
            Length(max=32)
            ]
        )
    password = OurTextField(
        widget=OurPasswordInput(),
        validators=[
            Required()
            ]
        )

class SearchPerformanceForm(OurForm):
    event_id = OurTextField(
        label=u'興行ID：',
    )
    event_code_1 = OurTextField(
        label=u'興行コード：',
        validators=[
            Length(max=6, message=u'6文字以内で入力してください')
        ]
    )
    event_code_2 = OurTextField(
        label=u'興行サブコード：',
        validators=[
            Length(max=4, message=u'4文字以内で入力してください')
        ]
    )
    event_name = OurTextField(
        label=u'興行名：',
    )
    performance_name = OurTextField(
        label=u'公演名：',
    )
    venue_name = OurTextField(
        label=u'会場名：',
    )
    performance_from = OurTextField(
        label=u'公演日：',
    )
    performance_to = OurTextField(
        label=u'公演日：',
    )