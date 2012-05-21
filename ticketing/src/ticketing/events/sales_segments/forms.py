# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms.validators import Required, Regexp, Length, Optional, ValidationError

from ticketing.utils import DateTimeField

class SalesSegmentForm(Form):

    id = HiddenField(
        label='',
        validators=[Optional()],
    )
    event_id = HiddenField(
        label='',
        validators=[Required(u'入力してください')]
    )
    name = TextField(
        label=u'販売区分名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    start_at = DateTimeField(
        label=u'販売開始日時',
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M'
    )
    end_at = DateTimeField(
        label=u'販売終了日時',
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M'
    )

    def validate_end_at(form, field):
        if field.data is not None and field.data < form.start_at.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')
