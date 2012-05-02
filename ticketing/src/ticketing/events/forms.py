# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, IntegerField
from wtforms.validators import Required, Regexp, Length, Optional, ValidationError

from ticketing.utils import DateTimeField

class EventForm(Form):
    code = TextField(
        label = u'公演コード',
        validators=[
            Required(u'入力してください'),
            Regexp(u'^[a-zA-Z0-9]*$', message=u'英数字のみ入力できます'),
            Length(max=12, message=u'12文字以内で入力してください'),
        ]
    )
    title = TextField(
        label = u'タイトル',
        validators=[
            Required(u'入力してください'),
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
    abbreviated_title = TextField(
        label = u'タイトル略称',
        validators=[
            Required(u'入力してください'),
            Length(max=100, message=u'100文字以内で入力してください'),
        ]
    )
    start_on = DateTimeField(
        label = u'開演日時',
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M'
    )
    end_on = DateTimeField(
        label = u'最終公演日時',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M'
    )

    def validate_end_on(form, field):
        if field.data is not None and field.data < form.start_on.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')
