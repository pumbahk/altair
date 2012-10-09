# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField, IntegerField, BooleanField
from wtforms.validators import Regexp, Length, Optional, ValidationError
from wtforms.widgets import CheckboxInput

from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import SalesSegmentKindEnum


## todo: move it
class MemberGroupForm(Form):
    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )

    name = TextField(
        label=u"名前"
        )

    is_guest = BooleanField(
        label=u"ゲストログイン"
        )

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
        label=u'販売区分表示名',
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
    upper_limit = IntegerField(
        label=u'購入上限枚数',
        default=10,
        validators=[Required()],
    )
    seat_choice = IntegerField(
        label=u'座席選択可',
        default=1,
        widget=CheckboxInput(),
    )
    public = IntegerField(
        label=u'一般販売',
        default=1,
        widget=CheckboxInput(),
    )
    copy = IntegerField(
        label='',
        default=0,
        widget=CheckboxInput(),
    )
    copy_payment_delivery_method_pairs = IntegerField(
        label=u'決済配送方法をコピーする',
        default=0,
        widget=CheckboxInput(),
    )
    copy_products = IntegerField(
        label=u'商品をコピーする',
        default=0,
        widget=CheckboxInput(),
    )

    def validate_end_at(form, field):
        if field.data is not None and field.data < form.start_at.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')
