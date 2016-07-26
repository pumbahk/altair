# -*- coding: utf-8 -*-

import logging

from wtforms import Form, TextField, SelectField, HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError, Email
from wtforms.compat import iteritems

from altair.formhelpers import (
    OurDateTimeField, Translations, Required, RequiredOnUpdate, MultipleEmail,
    OurForm, OurIntegerField, OurBooleanField, OurDecimalField, OurSelectField, OurTextAreaField,
    OurTimeField, PHPCompatibleSelectMultipleField, zero_as_none, after1900, Max,
    )
from altair.app.ticketing.core.models import Operator, ReportSetting, ReportRecipient, SalesSegment, Performance, Event
from altair.app.ticketing.core.models import ReportFrequencyEnum, ReportPeriodEnum, ReportTypeEnum

DETAIL_REPORT_SALES_SEGMENTS_LIMIT = 100


def validate_report_type(event_id, report_type):
    # 販売区分数が多いイベントは詳細レポートでの設定は不可
    if event_id and report_type == ReportTypeEnum.Detail.v[0]:
        count = SalesSegment.query.join(Performance).join(Event).filter(Event.id==event_id).count()
        if count > DETAIL_REPORT_SALES_SEGMENTS_LIMIT:
            raise ValidationError(u'レポート対象が多すぎます。レポート内容で"合計"を選択してください。')


def validate_from_to_date(label):
    msg_exist = label + u'の指定した期間を両方入力ください。'
    msg_wrong_date = label + u'の指定した期間が、不正です。'

    def _validate_from_to_date(form, field):
        this = field.id
        other = this.replace('from', 'to')
        
        if not form.data[this] and not form.data[other]:
            pass

        if form.data[this] and form.data[other]:
            if form.data[this] > form.data[other]:
                raise ValidationError(msg_wrong_date)
        elif form.data[this] or form.data[other]:
            raise ValidationError(msg_exist)

    return _validate_from_to_date


class SalesReportSearchForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(SalesReportSearchForm, self).__init__(formdata, obj, prefix, **kwargs)
        for name, field in iteritems(self._fields):
            if name in kwargs:
                field.data = kwargs[name]

    def _get_translations(self):
        return Translations()

    event_title = TextField(
        label=u'イベント名',
        validators=[Optional()],
    )

    event_from = OurDateTimeField(
        label=u'公演期間',
        validators=[validate_from_to_date(u'公演期間'), after1900],
        format='%Y-%m-%d %H:%M',
    )
    event_to = OurDateTimeField(
        label=u'公演期間',
        validators=[Optional(), after1900],
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
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
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
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
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
        format='%Y-%m-%d %H:%M',
    )

    limited_from = OurDateTimeField(
        label=u'絞り込み期間',
        validators=[validate_from_to_date(u'絞り込み期間'), after1900],
        format='%Y-%m-%d %H:%M',
    )
    limited_to = OurDateTimeField(
        label=u'絞り込み期間',
        validators=[Optional(), after1900],
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
        format='%Y-%m-%d %H:%M',
    )

    report_type = HiddenField(
        validators=[Optional()],
        default=ReportTypeEnum.Detail.v[0],
    )

    recipient = TextField(
        label=u'送信先',
        validators=[MultipleEmail()],
    )

    def validate_report_type(form, field):
        if field.data:
            validate_report_type(form.event_id.data, int(field.data))

    def is_detail_report(self):
        if not self.report_type.data:
            self.report_type.data = self.report_type.default
        return int(self.report_type.data) == ReportTypeEnum.Detail.v[0]

class NumberOfPerformanceReportExportForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(NumberOfPerformanceReportExportForm, self).__init__(formdata, obj, prefix, **kwargs)
        for name, field in iteritems(self._fields):
            if name in kwargs:
                field.data = kwargs[name]

    def _get_translations(self):
        return Translations()

    export_time_from = OurDateTimeField(
        label=u'絞り込み期間',
        validators=[Required(u"公演数CSV出力の販売開始日を入力して下さい。"), after1900],
        format='%Y-%m-%d %H:%M',
    )
    export_time_to = OurDateTimeField(
        label=u'絞り込み期間',
        validators=[Required(u"公演数CSV出力の販売終了日を入力して下さい。"), after1900],
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
        format='%Y-%m-%d %H:%M',
    )

    def validate_export_time_from(form, field):
        if form.data['export_time_from'] and form.data['export_time_to']:
            if form.data['export_time_from'] > form.data['export_time_to']:
                raise ValidationError(u'公演数CSV出力の指定した期間が、不正です')

class SalesReportForm(OurForm):

    def __init__(self, formdata=None, obj=None, prefix='', is_preview=False, **kwargs):
        super(SalesReportForm, self).__init__(formdata, obj, prefix, **kwargs)
        for name, field in iteritems(self._fields):
            if name in kwargs:
                field.data = kwargs[name]
        if formdata and not 'need_total' in formdata:
            self.need_total.data = True

        # previewの画面で集計期間の日付のエラーメッセージのみを出すためのflag
        self.is_preview = is_preview

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
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
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
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
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
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
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
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max),
        format='%Y-%m-%d %H:%M',
    )
    recipient = OurTextAreaField(
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
    report_type = HiddenField(
        validators=[Optional()],
        default=ReportTypeEnum.Detail.v[0],
    )

    def validate_report_type(form, field):
        if field.data:
            validate_report_type(form.event_id.data, int(field.data))

    def is_detail_report(self):
        if not self.report_type.data:
            self.report_type.data = self.report_type.default
        return int(self.report_type.data) == ReportTypeEnum.Detail.v[0]

    def _check_limited_from_to(self):
        status = True
        if self.limited_from.data and self.limited_to.data:
            status = self.limited_from.data <= self.limited_to.data
        if not status:
            self.limited_from.errors.append(u'開始日時は終了日時よりも前に設定してください。')
        return status

    def _preview_validate_msg(self):
        # プレビューの場合、件名と受信先のエラーメッセージを出さない。
        self.subject.errors = ()
        self.recipient.errors = ()

    def _rearrange_limited_after1990_msg(self):
        # 出力したい集計期間のエラーメッセージを整理する
        if self.limited_to.errors:
            msg_set = set()
            msg_set.update(self.limited_from.errors, self.limited_to.errors)

            # 重複しないため、全ての集計期間のエラーメッセージをlimited_fromに入れる
            self.limited_from.errors = list(msg_set)

            # limited_toのエラーメッセージをクリアする。
            self.limited_to.errors = []

    def validate(self, *args, **kwargs):
        status = super(self.__class__, self).validate(*args, **kwargs)
        self._rearrange_limited_after1990_msg()
        if not status and self.is_preview:
            self._preview_validate_msg()

        return all([status, self._check_limited_from_to()])

class ReportSettingForm(OurForm):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(ReportSettingForm, self).__init__(formdata, obj, prefix, **kwargs)

        context = kwargs.pop('context', None)
        self.context = context

        if obj:
            self.report_hour.data = int(obj.time[0:2] or 0)
            self.report_minute.data = int(obj.time[2:4] or 0)
        self.time.data = self.format_report_time()

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
    recipients = OurTextAreaField(
        label=u'送信先',
        validators=[Optional()],
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
    report_hour = SelectField(
        label=u'送信時刻',
        validators=[Required()],
        choices=[(h, u'%d' % h) for h in range(0, 24)],
        coerce=lambda v: None if not v else int(v)
    )
    report_minute = SelectField(
        label=u'',
        validators=[Required()],
        choices=[(h, u'%d' % h) for h in [0, 10, 20, 30, 40, 50]],
        default=10,
        coerce=lambda v: None if not v else int(v)
    )
    time = HiddenField(
        validators=[Optional()],
    )
    start_on = OurDateTimeField(
        label=u'送信開始日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    end_on = OurDateTimeField(
        label=u'送信終了日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(hour=Max, minute=Max, second=Max)
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

    def format_report_time(self, hour=None, minute=None):
        report_time = ''
        if hour is None:
            hour = self.report_hour.data
        if minute is None:
            minute = self.report_minute.data
        report_time = '{0:0>2}{1:0>2}'.format(hour, minute)
        report_time = report_time[0:3] + '0'
        return report_time

    def validate_frequency(form, field):
        if field.data:
            if field.data == ReportFrequencyEnum.Weekly.v[0] and not form.day_of_week.data:
                raise ValidationError(u'週次の場合は曜日を必ず選択してください')
            if field.data == ReportFrequencyEnum.Onetime.v[0] and (not form.start_on.data or not form.end_on.data):
                raise ValidationError(u'1回のみの場合は必ず送信開始日時/送信終了日時を指定してください')
            if field.data != ReportFrequencyEnum.Onetime.v[0] and form.report_minute.data == 0:
                raise ValidationError(u'0分に送信できるのは送信頻度で1回のみを指定した場合のみです')

    def validate_start_on(form, field):
        if field.data and form.end_on.data:
            if field.data > form.end_on.data:
                raise ValidationError(u'送信開始日時は送信終了日時よりも前に設定してください')

    def validate_report_type(form, field):
        if field.data:
            validate_report_type(form.event_id.data, int(field.data))

    def validate_event_id(form, field):
        if (field.data and form.performance_id.data) or (not field.data and not form.performance_id.data):
            raise ValidationError(u'エラーが発生しました')

    def process(self, formdata=None, obj=None, **kwargs):
        super(ReportSettingForm, self).process(formdata, obj, **kwargs)
        if not self.event_id.data:
            self.event_id.data = None
        if not self.performance_id.data:
            self.performance_id.data = None

    def validate_recipients(form, field):
        num = 0
        emails = []
        for line in field.data.splitlines():
            num += 1
            row = line.split(',')
            if len(row) > 2:
                raise ValidationError(u'入力された形式が不正です。（例：名前,メールアドレス {}行目'.format(str(num)))

            # メアドのみ
            if len(row) == 1:
                if not row[0].strip():
                    raise ValidationError(u'空白は指定できません。{}行目'.format(str(num)))

                if not validate_email(row[0].strip()):
                    raise ValidationError(u'メールアドレスの形式が不正です。{}行目'.format(str(num)))
                emails.append(row[0].strip())
                if not check_orverlap_email(emails):
                    raise ValidationError(u'メールアドレスが重複しています。{}行目'.format(str(num)))

            # 名前とメアド
            elif len(row) == 2:
                if not row[0].strip() or not row[1].strip():
                    raise ValidationError(u'空白は指定できません。{}行目'.format(str(num)))
                if not validate_email(row[1].strip()):
                    raise ValidationError(u'メールアドレスの形式が不正です。{}行目'.format(str(num)))
                emails.append(row[1].strip())
                if not check_orverlap_email(emails):
                    raise ValidationError(u'メールアドレスが重複しています。{}行目'.format(str(num)))

    def validate(self):
        status = super(ReportSettingForm, self).validate()
        if status:
            if not self.recipients.data:
                self.recipients.errors.append(u'送信先を入力してください')
                status = False
        return status


class OnlyEmailCheckForm(OurForm):
    email = TextField(
        label=u'メールアドレス',
        validators=[
            Required(),
            Email()
        ]
    )


def validate_email(data):
    check_form = OnlyEmailCheckForm()
    check_form.email.data = data
    if not check_form.validate():
        return False
    return True


def check_orverlap_email(emails):
    if len(set(emails)) != len(emails):
        return False
    return True
