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
    SelectField,
    SelectMultipleField,
    IntegerField
)
from wtforms.validators import Optional, AnyOf

logger = logging.getLogger(__name__)


class SearchFormBase(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        検索フォームの初期化：
        １（デフォルト）：orgに紐づくイベント一覧を取る。
        ２：イベントIDかパフォーマンスIDをkwargsにある場合、選択肢は該当イベントかパフォーマンスしか表示さない。
        """
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        self.request = kwargs.pop('request', None)
        organization = None
        event = None
        performance = None
        sales_segment_group = None

        if 'organization_id' in kwargs:
            organization_id = kwargs.pop('organization_id')
            organization = Organization.get(organization_id)

        if 'event_id' in kwargs:
            event_id = kwargs.pop('event_id')
            event = Event.get(event_id)

        if 'performance_id' in kwargs:
            performance_id = kwargs.pop('performance_id')
            performance = Performance.get(performance_id)

        if 'sales_segment_group_id' in kwargs:
            sales_segment_group_id = kwargs.pop('sales_segment_group_id')
            sales_segment_group = SalesSegmentGroup.get(sales_segment_group_id)

        ## Eventが指定されていなくて、Performanceが指定される場合のみ、紐づくEventを取る。
        if event is None and performance is not None:
            event = performance.event

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
                self.event_id.choices = [('', u'(イベントを選んでください。)')] + [(e.id, e.title) for e in events]
            ## Eventが指定される場合は該当Eventのみ表示する。
            else:
                self.event_id.choices = [(event.id, event.title)]

            ## Performanceが指定される場合は該当Performanceのみ表示する。
            if performance:
                dthelper = DateTimeHelper(create_date_time_formatter(self.request))
                self.performance_id.choices = [(performance.id, '%s (%s)' % (
                performance.name, dthelper.datetime(performance.start_on, with_weekday=True)))]

            ## SalesSegmentGroupが指定される場合は該当SaleSegmentGroupのみ表示する。
            if sales_segment_group:
                self.sales_segment_group_id.choices = [(sales_segment_group.id, sales_segment_group.name)]

        # 必ずEventは取得できるため
        if event:
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

    order_no = TextField(
        label=u'予約番号',
        validators=[Optional()],
    )
    payment_method = SelectMultipleField(
        label=u'決済方法',
        validators=[Optional()],
        choices=[],
        coerce=int,
    )
    delivery_method = SelectMultipleField(
        label=u'引取方法',
        validators=[Optional()],
        choices=[],
        coerce=int,
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
    name = TextField(
        label=u'氏名',
        validators=[Optional()],
    )
    tel = TextField(
        label=u'電話番号',
        validators=[Optional()],
    )
    email = TextField(
        label=u'メールアドレス',
        validators=[Optional()],
    )
    seat_number = TextField(
        label=u'座席番号',
        validators=[Optional()],
    )
    event_id = SelectField(
        label=u"イベント",
        coerce=lambda x : int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )
    performance_id = SelectField(
        label=u"公演",
        coerce=lambda x : int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )
    sales_segment_group_id = SelectMultipleField(
        label=u'販売区分グループ',
        coerce=lambda x : int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )
    refund_id = HiddenField(
        validators=[Optional()],
    )
    start_on_from = DateTimeField(
        label=u'公演日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateTimeWidget()
    )
    start_on_to = DateTimeField(
        label=u'公演日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max,
            hour=Max,
            minute=Max,
            second=Max,
            ),
        widget=OurDateTimeWidget()
    )
    sort = HiddenField(
        validators=[Optional()],
        default='order_no'
    )
    direction = HiddenField(
        validators=[Optional(), AnyOf(['asc', 'desc'], message='')],
        default='desc',
    )

    def get_conditions(self):
        conditions = {}
        for name, field in self._fields.items():
            if isinstance(field, HiddenField):
                continue
            if not field.data:
                continue

            if isinstance(field, SelectMultipleField) or isinstance(field, SelectField)\
               or isinstance(field, BugFreeSelectMultipleField):
                data = []
                for choice in field.choices:
                    if isinstance(field.data, list) and choice[0] in field.data:
                        data.append(choice[1])
                    elif choice[0] == field.data:
                        data.append(choice[1])
            else:
                data = field.data
            conditions[name] = (field.label.text, data)
        return conditions


class OrderSearchForm(SearchFormBase):
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
