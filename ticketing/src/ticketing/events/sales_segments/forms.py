# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField, IntegerField, BooleanField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput

from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import SalesSegmentKindEnum

class SalesSegmentForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()]
    )
    kind = SelectField(
        label=u'販売区分',
        validators=[Required()],
        choices=[(kind.k, kind.v) for kind in SalesSegmentKindEnum],
        coerce=str,
    )
    name = TextField(
        label=u'販売区分名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    start_at = DateTimeField(
        label=u'販売開始日時',
        validators=[Required()],
        format='%Y-%m-%d %H:%M'
    )
    end_at = DateTimeField(
        label=u'販売終了日時',
        validators=[Required()],
        format='%Y-%m-%d %H:%M'
    )
    payment_due_at = DateTimeField(
        label=u'入金期限',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M'
    )
    issuing_start_at = DateTimeField(
        label=u'発券開始日時',
        validators=[],
        format='%Y-%m-%d %H:%M'
    )
    issuing_end_at = DateTimeField(
        label=u'発券終了日時',
        validators=[],
        format='%Y-%m-%d %H:%M'
    )
    upper_limit = IntegerField(
        label=u'購入上限枚数',
        validators=[Optional()],
    )
    seat_choice = IntegerField(
        label=u'座席選択可',
        default=1,
        widget=CheckboxInput(),
    )

    def validate_end_at(form, field):
        if field.data is not None and field.data < form.start_at.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')


    def validate_issuing_start_at(form, field):
        if field.data is not None:
            if field.data >= form.issuing_end_at.data:
                raise ValidationError(u'発券終了日時より未来の日時は入力できません')
            if field.data < form.start_at.data:
                raise ValidationError(u'発売開始日より過去の日時は入力できません')


    def validate_issuing_end_at(form, field):
        if field.data is not None and field.data <= form.issuing_start_at.data:
            raise ValidationError(u'発券開始日時より過去の日時は入力できません')

