# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import Event, Organization, Operator, ReportSetting
from ticketing.core.models import ReportFrequencyEnum


class SalesReportForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

        if 'event_id' in kwargs:
            self.event_id.data = kwargs['event_id']
        if 'performance_id' in kwargs:
            self.performance_id.data = kwargs['performance_id']
        if 'sales_segment_id' in kwargs:
            self.sales_segment_id.data = kwargs['sales_segment_id']

    def _get_translations(self):
        return Translations()
   
    event_id = HiddenField(
        validators=[Optional()],
    )
    performance_id = HiddenField(
        validators=[Optional()],
    )
    sales_segment_id = HiddenField(
        validators=[Optional()],
    )
    limited_from = DateTimeField(
        label=u'絞り込み期間',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    limited_to = DateTimeField(
        label=u'絞り込み期間',
        validators=[Optional()],
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

    def validate_operator_id(form, field):
        count = ReportSetting.query.filter(
            ReportSetting.operator_id==field.data,
            ReportSetting.frequency==form.frequency.data,
            ReportSetting.event_id==form.event_id.data
        ).count()
        if count > 0:
           raise ValidationError(u"既に登録済みのオペレーターです")

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
        choices=[(kind.v, kind.k) for kind in ReportFrequencyEnum],
        coerce=int
    )
