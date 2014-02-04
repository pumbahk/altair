# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from altair.formhelpers import Translations, Required, JISX0208, after1900
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, OurIntegerField, OurBooleanField, DateField, DateTimeField
from altair.formhelpers.widgets import OurTextInput, OurDateWidget
from altair.formhelpers.filters import replace_ambiguous, zero_as_none
from altair.app.ticketing.helpers import label_text_for
from altair.app.ticketing.core.models import Event, EventSetting, Account

class EventSearchForm(OurForm):
    def _get_translations(self):
        return Translations()

    event_name_or_code = OurTextField(
        label=u'イベント名　または　コード',
        widget=OurTextInput()
        )

    performance_name_or_code = OurTextField(
        label=u'パフォーマンス名　または　コード',
        widget=OurTextInput()
        )

    perf_range_start = DateTimeField(
        label=u'公演期間検索',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    perf_range_end = DateTimeField(
        label=u'',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    deal_range_start = DateTimeField(
        label=u'販売期間検索',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    deal_range_end = DateTimeField(
        label=u'',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    perf_open_start = DateTimeField(
        label=u'公演開始日検索',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    perf_open_end = DateTimeField(
        label=u'',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    perf_close_start = DateTimeField(
        label=u'公演終了日検索',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    perf_close_end = DateTimeField(
        label=u'',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    deal_open_start = DateTimeField(
        label=u'販売開始日検索',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    deal_open_end = DateTimeField(
        label=u'',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    deal_close_start = DateTimeField(
        label=u'販売終了日検索',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    deal_close_end = DateTimeField(
        label=u'',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    lot_only = OurBooleanField(
        label=u'抽選を含むイベントを選択'
        )

class EventForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.account_id.choices = [
                (account.id, account.name) for account in Account.filter_by(organization_id=kwargs['organization_id'])
            ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    account_id = SelectField(
        label=u'配券元',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    code = TextField(
        label = u'イベントコード',
        validators=[
            Required(),
            Regexp(u'^[A-Z0-9]*$', message=u'英数字大文字のみ入力できます'),
        ]
    )
    title = TextField(
        label = u'タイトル',
        filters=[
            replace_ambiguous,
            ],
        validators=[
            Required(),
            JISX0208, 
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
    abbreviated_title = TextField(
        label = u'タイトル略称',
        filters=[
            replace_ambiguous,
            ],
        validators=[
            Required(),
            JISX0208, 
            Length(max=100, message=u'100文字以内で入力してください'),
        ]
    )
    order_limit = OurIntegerField(
        label=label_text_for(EventSetting.order_limit),
        default=None,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    max_quantity_per_user = OurIntegerField(
        label=label_text_for(EventSetting.max_quantity_per_user),
        default=None,
        filters=[zero_as_none],
        validators=[Optional()]
    )
    original_id = HiddenField(
        validators=[Optional()],
    )
    display_order = OurIntegerField(
        label=label_text_for(Event.display_order),
        default=1,
        hide_on_new=True,
        )

    def validate_code(form, field):
        if field.data:
            expected_len = {7}
            query = Event.filter(Event.code==field.data)
            if form.id and form.id.data:
                event = Event.query.filter_by(id=form.id.data).one()
                expected_len.add(len(event.code)) # 古いコード体系(7桁)と新しいコード体系(5桁)のどちらも許容する
                query = query.filter(Event.id!=form.id.data) # いま編集中のもの以外で
            if len(field.data) not in expected_len:
                raise ValidationError(u'%s入力してください' % u'もしくは'.join(u'%d文字' % l for l in expected_len))
            if query.count() > 0:
                raise ValidationError(u'既に使用されています')
