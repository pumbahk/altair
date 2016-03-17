# -*- coding: utf-8 -*-

from .performances.api import get_no_ticket_bundles

from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField
from wtforms.validators import Regexp, Length, NumberRange, Optional, ValidationError

from altair.formhelpers import Translations, Required, JISX0208, after1900
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurTextField, OurIntegerField, OurBooleanField, DateField, DateTimeField, OurSelectField
from altair.formhelpers.widgets import OurTextInput, OurDateWidget
from altair.formhelpers.filters import replace_ambiguous, zero_as_none, blank_as_none
from altair.app.ticketing.helpers import label_text_for
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Event, EventSetting, Account
from altair.app.ticketing.cart.models import CartSetting
from altair.app.ticketing.payments.plugins.sej import DELIVERY_PLUGIN_ID as SEJ_DELIVERY_PLUGIN_ID
from altair.app.ticketing.core.utils import ApplicableTicketsProducer

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
        label=u'受付期間検索',
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
        label=u'受付開始日検索',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    deal_open_end = DateTimeField(
        label=u'',
        validators=[Optional(), after1900],
        widget=OurDateWidget()
        )

    deal_close_start = DateTimeField(
        label=u'受付終了日検索',
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

class EventForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        context = kwargs.pop('context')
        super(EventForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.context = context
        if self.cart_setting_id.data is None:
            self.cart_setting_id.data = self.context.organization.setting.cart_setting_id

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    account_id = OurSelectField(
        label=u'配券元',
        validators=[Required(u'選択してください')],
        choices=lambda field: [(str(account.id), account.name) for account in Account.query.filter_by(organization_id=field._form.context.organization.id)],
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
    middle_stock_threshold = OurIntegerField(
        label=label_text_for(EventSetting.middle_stock_threshold),
        default=None,
        filters=[zero_as_none],
        validators=[Optional()],
        hide_on_new=True,
        help=u'カートの在庫表示を△にする閾値を席数で指定します。在庫数がこの値未満(未設定の場合は20未満)になると△表示になります。'
    )
    middle_stock_threshold_percent = OurIntegerField(
        label=label_text_for(EventSetting.middle_stock_threshold_percent),
        default=None,
        filters=[zero_as_none],
        validators=[Optional(), NumberRange(min=1, max=100, message=u'1〜100%まで入力できます')],
        hide_on_new=True,
        help=u'カートの在庫表示を△にする閾値を在庫数に対するパーセンテージで指定します。在庫数がこの値未満(未設定の場合は50%未満)になると△表示になります。'
    )
    original_id = HiddenField(
        validators=[Optional()],
    )
    display_order = OurIntegerField(
        label=label_text_for(Event.display_order),
        default=1,
        hide_on_new=True,
    )
    cart_setting_id = OurSelectField(
        label=label_text_for(EventSetting.cart_setting_id),
        default=lambda field: field.context.organization.setting.cart_setting_id,
        choices=lambda field: [(str(cart_setting.id), (cart_setting.name or u'(名称なし)')) for cart_setting in DBSession.query(CartSetting).filter_by(organization_id=field._form.context.organization.id)],
        coerce=int
        )
    visible = OurBooleanField(
        label=u'イベントの表示／非表示',
        default=True,
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

    def validate_display_order(form, field):
        if -2147483648 > field.data or field.data > 2147483647:
            raise ValidationError(u'-2147483648から、2147483647の間で指定できます。')


class EventPublicForm(Form):

    event_id = HiddenField(
        label='',
        validators=[Optional()],
    )
    public = HiddenField(
        label='',
        validators=[Required()],
    )

    def validate_public(form, field):
        # 公開する場合のみチェック
        if field.data == 1:
            # 配下の全てのProductItemに券種が紐づいていること
            event = Event.get(form.event_id.data)
            error_msg = []
            for performance in event.performances:

                no_ticket_bundles = get_no_ticket_bundles(performance)

                if no_ticket_bundles:
                    error_msg.append(u'パフォーマンス[%s]券面構成が設定されていない商品設定がある為、公開できません %s' % (performance.name, no_ticket_bundles))
            if len(error_msg) > 0:
                raise ValidationError(('\n').join(error_msg))
