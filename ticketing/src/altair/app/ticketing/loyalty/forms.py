# encoding: utf-8

from wtforms.fields import HiddenField
from wtforms.validators import Optional, NumberRange
from altair.app.ticketing.helpers import label_text_for
from altair.formhelpers import Translations
from altair.formhelpers.form import OurForm
from altair.formhelpers.validators import Required
from altair.formhelpers.fields import OurTextField, OurDecimalField, OurDateField, OurDateTimeField, PercentageField, OurSelectField, OurGroupedSelectMultipleField
from altair.formhelpers.widgets.datetime import OurDateWidget
from altair.app.ticketing.users import models as user_models
from wtforms.fields import TextAreaField
from wtforms.validators import ValidationError
from .models import PointGrantSetting, PointGrantHistoryEntry
from ..models import HyphenationCodecMixin
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import asc, and_
from ..core.models import Event, Product, SalesSegmentGroup, SalesSegment
from . import helpers as lh

from datetime import date, datetime


def append_error(field, error):
    if not hasattr(field.errors, 'append'):
        field.errors = list(field.errors)
    field.errors.append(error)


class PointGrantSettingForm(OurForm):
    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=label_text_for(PointGrantSetting.id),
        validators=[Optional()]
        )

    name = OurTextField(
        label=label_text_for(PointGrantSetting.name),
        validators=[Required()]
        )

    type = OurSelectField(
        label=label_text_for(PointGrantSetting.type),
        choices=[(v.v, lh.format_point_type(v.v)) for v in user_models.UserPointAccountTypeEnum._values],
        coerce=long
        )

    fixed = OurDecimalField(
        label=label_text_for(PointGrantSetting.fixed),
        validators=[Optional()]
        )

    rate = PercentageField(
        label=label_text_for(PointGrantSetting.rate),
        validators=[Optional()],
        precision=0
        )

    start_at = OurDateTimeField(
        label=label_text_for(PointGrantSetting.start_at),
        validators=[Optional()]
        )

    end_at = OurDateTimeField(
        label=label_text_for(PointGrantSetting.end_at),
        validators=[Optional()]
        )

    def validate_name(self, field):
        if PointGrantSetting.query.filter(and_(PointGrantSetting.name == field.data, PointGrantSetting.organization_id == self.context.user.organization_id, PointGrantSetting.id != (self.context.point_grant_setting and self.context.point_grant_setting.id or None))).first() is not None:
            raise ValidationError(u'同じ名前の設定が既に存在します')

    def _validate_rate(self):
        if not self.rate.data and not self.fixed.data:
            self.rate.errors.append(u'{}と{}の両方が空です'.format(self.fixed.label.text, self.rate.label.text))
            return False
        return True

    def _validate_start_at(self):
        return validate_datetime(self.start_at)

    def _validate_end_at(self):
        return validate_datetime(self.end_at)

    def validate(self, *args, **kwargs):
        return all([
            super(self.__class__, self).validate(*args, **kwargs),
            self._validate_rate(),
            self._validate_start_at(),
            self._validate_end_at(),
         ])

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', None)
        super(PointGrantSettingForm, self).__init__(*args, **kwargs)


def validate_datetime(field):
    if not field.data:
        return True

    try:
        field.data.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        field.errors.append(u'{}が、不正な日付です'.format(field.label.text))
        return False
    return True


class PointGrantHistoryEntryForm(OurForm):
    submitted_on = OurDateField(
        label=u'ポイント付与予定日',
        validators=[Required(u'ポイント付与予定日の値が不正です')],
        format='%Y-%m-%d',
        widget=OurDateWidget()
        )

    amount = OurDecimalField(
        label=u'付与ポイント',
        validators=[Required(u'付与ポイントの値が不正です'), NumberRange(min=0, message=u'付与ポイントの値が不正です')]
        )

    def __init__(self, formdata=None, obj=None, prefix='', membergroups=None, **kwargs):
        super(PointGrantHistoryEntryForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.context = kwargs.pop('context', None)

    def validate_submitted_on(self, field):
        if field.data < date.today():
            raise ValidationError(u'%sには過去の日付は指定できません' % self.submitted_on.label.text)


class PointGrantHistoryEntryImportForm(OurForm):
    csv_data = TextAreaField(
        label=u'CSVデータ(予約番号,付与ポイント)',
        validators=[Required(u'CSVデータが空です')]
    )

    submitted_on = OurDateField(
        label=u'ポイント付与予定日',
        validators=[Required(u'ポイント付与予定日の値が不正です')],
        format='%Y-%m-%d',
        widget=OurDateWidget()
    )

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', None)
        super(PointGrantHistoryEntryImportForm, self).__init__(*args, **kwargs)

    def validate_submitted_on(self, field):
        if field.data < date.today():
            raise ValidationError(u'%sには過去の日付は指定できません' % self.submitted_on.label.text)