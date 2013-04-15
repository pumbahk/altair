# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError

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
            self.operator_id.choices = operators

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
        validators=[Required()],
        choices=[],
        coerce=int
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
        default=1,
        choices=[
            ('', ''),
            (0, u'月'),
            (1, u'火'),
            (2, u'水'),
            (3, u'木'),
            (4, u'金'),
            (5, u'土'),
            (6, u'日'),
        ],
        coerce=lambda v: None if not v else int(v)
    )
    time = SelectField(
        label=u'送信時間',
        validators=[Required()],
        default=7,
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
        count = ReportSetting.query.filter(
            ReportSetting.operator_id==field.data,
            ReportSetting.frequency==form.frequency.data,
            ReportSetting.event_id==form.event_id.data,
            ReportSetting.day_of_week==form.day_of_week.data,
            ReportSetting.time==form.time.data
        ).count()
        if count > 0:
            raise ValidationError(u"既に登録済みのオペレーターです")
