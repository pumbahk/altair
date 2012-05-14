# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField
from wtforms.validators import Required, Regexp, Length, Optional, ValidationError

from ticketing.utils import DateTimeField

class SalesSegmentForm(Form):

    name = TextField(
        label=u'販売区分名',
        validators=[Required(u'入力してください')]
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
