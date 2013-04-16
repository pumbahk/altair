# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError, Email

from ticketing.formhelpers import DateTimeField, Translations, Required, after1900
from ticketing.core.models import Event, Organization, Operator, ReportSetting
from ticketing.core.models import ReportFrequencyEnum


class SalesReportForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

        if 'event_id' in kwargs:
            self.event_id.data = kwargs['event_id']
        if 'performance_id' in kwargs:
            self.performance_id.data = kwargs['performance_id']
        if 'sales_segment_group_id' in kwargs:
            self.sales_segment_group_id.data = kwargs['sales_segment_group_id']

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
    limited_from = DateTimeField(
        label=u'絞り込み期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    limited_to = DateTimeField(
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


class SalesReportMailForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

        if 'event_id' in kwargs and 'organization_id' in kwargs:
            operators = Operator.query.join(Organization).join(Event)\
                                .filter(Operator.organization_id==kwargs['organization_id'])\
                                .filter(Event.id==kwargs['event_id'])\
                                .with_entities(Operator.id, Operator.name).all()
            self.operator_id.choices = [('', '')] + operators

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        validators=[Optional()],
    )
    event_id = HiddenField(
        validators=[Required()],
    )
    operator_id = SelectField(
        label=u'オペレータ',
        validators=[],
        choices=[],
        coerce=lambda v: '' if not v else int(v)
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
        choices=[('', '')] + [(h, u'%d時' % h) for h in range(0, 24)],
        coerce=lambda v: None if not v else int(v)
    )
    start_on = DateTimeField(
        label=u'開始日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )
    end_on = DateTimeField(
        label=u'終了日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
    )

    def validate_operator_id(form, field):
        if not field.data and not form.email.data:
            raise ValidationError(u'オペレーター、またはメールアドレスのいずれかを入力してください')
        if field.data and form.email.data:
            raise ValidationError(u'オペレーター、メールアドレスの両方を入力することはできません')

        if field.data:
            query = ReportSetting.query.filter(
                ReportSetting.event_id==form.event_id.data,
                ReportSetting.frequency==form.frequency.data,
                ReportSetting.time==form.time.data,
                ReportSetting.operator_id==field.data
            )
            if form.day_of_week.data == ReportFrequencyEnum.Weekly.v[0]:
                query = query.filter(ReportSetting.day_of_week==form.day_of_week.data)
            if query.count() > 0:
                raise ValidationError(u'既に登録済みのオペレーターです')

    def validate_email(form, field):
        if field.data:
            query = ReportSetting.query.filter(
                ReportSetting.event_id==form.event_id.data,
                ReportSetting.frequency==form.frequency.data,
                ReportSetting.time==form.time.data,
                ReportSetting.email==form.email.data
            )
            if form.frequency.data == ReportFrequencyEnum.Weekly.v[0]:
                query = query.filter(ReportSetting.day_of_week==form.day_of_week.data)
            if query.count() > 0:
                raise ValidationError(u'既に登録済みのメールアドレスです')

    def validate_frequency(form, field):
        if field.data:
            if field.data == ReportFrequencyEnum.Weekly.v[0] and not form.day_of_week.data:
                raise ValidationError(u'週次の場合は曜日を必ず選択してください')
