# -*- coding: utf-8 -*-

import logging

from wtforms import Form, TextField, SelectField, HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError, Email
from wtforms.compat import iteritems

from altair.formhelpers import (
    OurDateTimeField, Translations, Required, RequiredOnUpdate,
    OurForm, OurIntegerField, OurBooleanField, OurDecimalField, OurSelectField,
    OurTimeField, zero_as_none, after1900)
from altair.app.ticketing.core.models import Operator, ReportSetting
from altair.app.ticketing.core.models import ReportFrequencyEnum, ReportPeriodEnum, ReportTypeEnum


class SalesReportForm(OurForm):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(type(self), self).__init__(formdata, obj, prefix, **kwargs)
        for name, field in iteritems(self._fields):
            if name in kwargs:
                field.data = kwargs[name]
        self.need_total.data = True

    def _get_translations(self):
        return Translations()

    event_id = HiddenField(
        validators=[Optional()],
    )
    performance_id = HiddenField(
        validators=[Optional()],
    )
    sales_segment_group_id = HiddenField(
        validators=[Optional()],
    )
    event_title = TextField(
        label=u'イベント名',
        validators=[Optional()],
    )
    event_from = OurDateTimeField(
        label=u'公演期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    event_to = OurDateTimeField(
        label=u'公演期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    event_start_from = OurDateTimeField(
        label=u'公演開始日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    event_start_to = OurDateTimeField(
        label=u'公演開始日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    event_end_from = OurDateTimeField(
        label=u'公演終了日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    event_end_to = OurDateTimeField(
        label=u'公演終了日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    limited_from = OurDateTimeField(
        label=u'絞り込み期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    limited_to = OurDateTimeField(
        label=u'絞り込み期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    recipient = TextField(
        label=u'送信先',
        validators=[Required()],
    )
    subject = TextField(
        label=u'件名',
        validators=[Required()],
    )
    need_total = OurBooleanField(
        validators=[Optional()],
        default=True,
    )
    recent_report = OurBooleanField(
        validators=[Optional()],
        default=False,
    )
    report_type = HiddenField(
        validators=[Optional()],
        default=ReportTypeEnum.Detail.v[0],
    )

    def is_detail_report(self):
        if not self.report_type.data:
            self.report_type.data = self.report_type.default
        return int(self.report_type.data) == ReportTypeEnum.Detail.v[0]


class ReportSettingForm(OurForm):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(type(self), self).__init__(formdata, obj, prefix, **kwargs)

        context = kwargs.pop('context', None)
        self.context = context

        if context.user.organization_id:
            operators = Operator.query.filter_by(organization_id=context.user.organization_id).all()
            self.operator_id.choices = [('', '')] + [(o.id, o.name) for o in operators]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Optional()],
    )
    performance_id = HiddenField(
        validators=[Optional()],
    )
    operator_id = SelectField(
        label=u'オペレータ',
        validators=[Optional()],
        choices=[],
        coerce=lambda v: None if not v else int(v)
    )
    name = TextField(
        label=u'名前',
        validators=[
            Optional(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    email = TextField(
        label=u'メールアドレス',
        validators=[
            Optional(),
            Email()
        ]
    )
    frequency = SelectField(
        label=u'送信頻度',
        validators=[Required()],
        choices=[(kind.v[0], kind.v[1]) for kind in ReportFrequencyEnum],
        coerce=int
    )
    day_of_week = SelectField(
        label=u'送信曜日',
        validators=[Optional()],
        choices=[
            ('', ''),
            (1, u'月'),
            (2, u'火'),
            (3, u'水'),
            (4, u'木'),
            (5, u'金'),
            (6, u'土'),
            (7, u'日'),
        ],
        coerce=lambda v: None if not v else int(v)
    )
    time = SelectField(
        label=u'送信時間',
        validators=[Required()],
        choices=[(h, u'%d時' % h) for h in range(0, 24)],
        coerce=lambda v: None if not v else int(v)
    )
    start_on = OurDateTimeField(
        label=u'開始日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    end_on = OurDateTimeField(
        label=u'終了日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    period = SelectField(
        label=u'レポート対象期間',
        validators=[Required()],
        choices=sorted([(kind.v[0], kind.v[1]) for kind in ReportPeriodEnum]),
        coerce=int
    )
    report_type = SelectField(
        label=u'レポート内容',
        validators=[Required()],
        choices=sorted([(kind.v[0], kind.v[1]) for kind in ReportTypeEnum]),
        coerce=int
    )

    def validate_operator_id(form, field):
        if field.data:
            query = ReportSetting.query.filter(
                ReportSetting.frequency==form.frequency.data,
                ReportSetting.time==form.time.data,
                ReportSetting.operator_id==field.data
            )
            if form.id.data:
                query = query.filter(ReportSetting.id!=form.id.data)
            if form.event_id.data:
                query = query.filter(ReportSetting.event_id==form.event_id.data)
            if form.performance_id.data:
                query = query.filter(ReportSetting.performance_id==form.performance_id.data)
            if form.day_of_week.data == ReportFrequencyEnum.Weekly.v[0]:
                query = query.filter(ReportSetting.day_of_week==form.day_of_week.data)
            if query.count() > 0:
                raise ValidationError(u'既に登録済みのオペレーターです')

    def validate_email(form, field):
        if field.data:
            query = ReportSetting.query.filter(
                ReportSetting.frequency==form.frequency.data,
                ReportSetting.time==form.time.data,
                ReportSetting.email==form.email.data
            )
            if form.id.data:
                query = query.filter(ReportSetting.id!=form.id.data)
            if form.event_id.data:
                query = query.filter(ReportSetting.event_id==form.event_id.data)
            if form.performance_id.data:
                query = query.filter(ReportSetting.performance_id==form.performance_id.data)
            if form.frequency.data == ReportFrequencyEnum.Weekly.v[0]:
                query = query.filter(ReportSetting.day_of_week==form.day_of_week.data)
            if query.count() > 0:
                raise ValidationError(u'既に登録済みのメールアドレスです')

    def validate_frequency(form, field):
        if field.data:
            if field.data == ReportFrequencyEnum.Weekly.v[0] and not form.day_of_week.data:
                raise ValidationError(u'週次の場合は曜日を必ず選択してください')

    def process(self, formdata=None, obj=None, **kwargs):
        super(type(self), self).process(formdata, obj, **kwargs)
        if not self.event_id.data:
            self.event_id.data = None
        if not self.performance_id.data:
            self.performance_id.data = None

    def validate(self):
        status = super(type(self), self).validate()
        if status:
            # event_id or performance_id のどちらか必須
            if (self.event_id.data and self.performance_id.data) or (not self.event_id.data and not self.performance_id.data):
                self.event_id.errors.append(u'エラーが発生しました')
                status = False
            # operator_id or email のどちらか必須
            email_length = len(self.email.data) if self.email.data else 0
            if not self.operator_id.data and email_length == 0:
                self.operator_id.errors.append(u'オペレーター、またはメールアドレスのいずれかを入力してください')
                status = False
            if self.operator_id.data and email_length > 0:
                self.operator_id.errors.append(u'オペレーター、メールアドレスの両方を入力することはできません')
                status = False
        return status
