# -*- coding: utf-8 -*-

import logging
from wtforms import TextField, SelectField, IntegerField, DecimalField, SelectMultipleField, HiddenField, BooleanField
from wtforms.validators import Length, NumberRange, EqualTo, Optional, ValidationError
from wtforms import RadioField
from wtforms.widgets import TextInput, html_params

from altair.formhelpers import (
    Translations,
    Required,
    OurForm,
    )
from altair.formhelpers.fields import (
    BugFreeSelectField,
    OurTextField,
    OurSelectField,
    OurIntegerField,
    OurBooleanField,
    OurRadioField,
    OurDecimalField,
    NullableTextField,
    OurPHPCompatibleSelectMultipleField,
    BugFreeSelectMultipleField,
    )
from altair.formhelpers.widgets import (
    OurDateWidget,
    OurDateTimeWidget,
    CheckboxMultipleSelect,
    OurListWidget,
    )
from altair.formhelpers.validators import JISX0208
from altair.app.ticketing.helpers import label_text_for
from altair.formhelpers.fields import OurTextField, OurIntegerField, OurDecimalField, OurSelectField, OurBooleanField, OurField

logger = logging.getLogger(__name__)


class SalesSearchForm(OurForm):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(SalesSearchForm, self).__init__(formdata, obj, prefix, **kwargs)
        if "sales_report_operators" in kwargs:
            self.operators.choices = kwargs['sales_report_operators']

    sales_kind = OurSelectField(
        label=u"検索区分",
        validators=[Optional()],
        choices=[(u'sales_start', u"販売開始日"), (u'lots_announce_time', u"抽選結果発表予定日")]
        )
    sales_term = OurSelectField(
        label=u"期間",
        validators=[Optional()],
        choices=[
            (u"today", u"今日"),
            (u"tomorrow", u"明日"),
            (u"this_week", u"今週（月〜日）"),
            (u"this_week_plus_monday", u"今週（月〜月）"),
            (u"next_week", u"来週（月〜日）"),
            (u"next_week_plus_monday", u"来週（月〜月）"),
            (u"this_month", u"今月"),
            (u"term", u"期間指定"),
        ]
    )
    salessegment_group_kind = BugFreeSelectMultipleField(
        label=u'販売区分',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        choices=[
            ('normal', u'一般発売'),
            ('early_lottery', u'先行抽選'),
            ('early_firstcome', u'先行先着')
        ],
        coerce=str,
    )
    operators = BugFreeSelectMultipleField(
        label=u'担当',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        coerce=str,
    )


