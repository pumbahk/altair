# -*- coding: utf-8 -*-

import logging

from altair.app.ticketing.core.models import (
    Organization,
    PaymentMethod,
    DeliveryMethod,
    SalesSegmentGroup,
    Performance,
    Event,
)
from altair.formhelpers import (
    Max,
    after1900)
from altair.formhelpers.fields import (
    DateTimeField,
    BugFreeSelectMultipleField,
)
from altair.formhelpers.widgets import (
    OurDateTimeWidget,
    CheckboxMultipleSelect,
)
from altair.viewhelpers.datetime_ import create_date_time_formatter, DateTimeHelper
from wtforms import Form
from wtforms.fields import (
    HiddenField,
    TextField,
    IntegerField
)
from wtforms.validators import Optional, AnyOf

from ..orders.forms import OrderSearchForm

logger = logging.getLogger(__name__)


class MiniAdminOrderSearchForm(OrderSearchForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        検索フォームの初期化：
        １（デフォルト）：orgに紐づくイベント一覧を取る。
        ２：イベントIDかパフォーマンスIDをkwargsにある場合、選択肢は該当イベントかパフォーマンスしか表示さない。
        """
        Form.__init__(self, formdata, obj, prefix, **kwargs)

        organization = None
        event = None

        self.request = kwargs.pop('request', None)
        self.event_id.data = kwargs.pop('event_id', None)

        if self.event_id.data:
            event = Event.get(self.event_id.data)

        if 'organization_id' in kwargs:
            organization_id = kwargs.pop('organization_id')
            organization = Organization.get(organization_id)

        ## Organizationが取得されなくて、Eventが取得される場合は、紐づくOrganizationを取る。
        if organization is None and event is not None:
            organization = event.organization

        # organiztion_id, event_idかperformance_idのいずれがkwagrsにあると、organizationを取得できる。
        if organization:
            self.payment_method.choices = [(pm.id, pm.name) for pm in
                                           PaymentMethod.filter_by_organization_id(organization.id)]
            self.delivery_method.choices = [(dm.id, dm.name) for dm in
                                            DeliveryMethod.filter_by_organization_id(organization.id)]

            ## Eventが指定されていない場合はorgに紐づくEvent一覧をとる。
            if event is None:
                events = Event.query.with_entities(Event.id, Event.title) \
                    .filter(Event.organization_id == organization.id) \
                    .order_by(Event.created_at.desc())
                self.event_id.choices = [(e.id, e.title) for e in events]
            ## Eventが指定される場合は該当Eventのみ表示する。
            else:
                self.event_id.choices = [(event.id, event.title)]

        if self.event_id.data:
            dthelper = DateTimeHelper(create_date_time_formatter(self.request))
            performances = Performance.query.join(Event) \
                .filter(Event.id == self.event_id.data) \
                .order_by(Performance.created_at.desc())
            self.performance_id.choices = [('', u'')] + [
                (p.id, '%s (%s)' % (p.name, dthelper.datetime(p.start_on, with_weekday=True))) for p in
                performances]

            sales_segment_groups = SalesSegmentGroup.query.filter(SalesSegmentGroup.event_id == self.event_id.data)
            self.sales_segment_group_id.choices = [(sales_segment_group.id, sales_segment_group.name) for
                                                   sales_segment_group in sales_segment_groups]

        # イベントは必ず一意に決まるため、最初に選択しておく
        self.event_id.data = self.event_id.choices[0][0]

    fm_reserve_number = TextField(
        label=u'FM予約番号',
        validators=[Optional()],
    )

    billing_or_exchange_number = TextField(
        label=u'SEJ払込票/引換票番号',
        validators=[Optional()],
    )
    ordered_from = DateTimeField(
        label=u'予約日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateTimeWidget()
    )
    ordered_to = DateTimeField(
        label=u'予約日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max,
            hour=Max,
            minute=Max,
            second=Max
        ),
        widget=OurDateTimeWidget()
    )
    status = BugFreeSelectMultipleField(
        label=u'ステータス',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        choices=[
            ('ordered', u'受付済み'),
            ('delivered', u'配送済み'),
            ('canceled', u'キャンセル'),
        ],
        coerce=str,
    )
    issue_status = BugFreeSelectMultipleField(
        label=u'発券ステータス',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        choices=[
            ('issued', u'発券済み'),
            ('unissued', u'未発券'),
        ],
        coerce=str,
    )
    payment_status = BugFreeSelectMultipleField(
        label=u'決済ステータス',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        choices=[
            ('unpaid', u'未入金'),
            ('paid', u'入金済み'),
            ('refunding', u'払戻予約'),
            ('refunded', u'払戻済み')
        ],
        coerce=str,
    )
    mail_magazine_status = BugFreeSelectMultipleField(
        label=u'メールマガジン受信可否',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Optional()],
        choices=[
            ('subscribed', u'メルマガ受信可'),
            ('unsubscribed', u'メルマガ受信不可')
        ],
        coerce=str,
    )
    login_id = TextField(
        label=u'ログインID',
        validators=[Optional()],
    )
    member_id = TextField(
        label=u'会員番号',
        validators=[Optional()],
    )
    sort = HiddenField(
        validators=[Optional()],
        default='order_no'
    )
    direction = HiddenField(
        validators=[Optional(), AnyOf(['asc', 'desc'], message='')],
        default='desc',
    )
    number_of_tickets = IntegerField(
        label=u'購入枚数',
        validators=[Optional()]
    )
