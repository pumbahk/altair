# -*- coding: utf-8 -*-

import logging
import re
import itertools
import decimal
import csv
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from pyramid.security import has_permission, ACLAllowed
from paste.util.multidict import MultiDict
from wtforms import Form, ValidationError, BooleanField
from wtforms.fields import (
    Field,
    HiddenField,
    TextField,
    SelectField,
    SelectMultipleField,
    TextAreaField,
    RadioField,
    FormField,
    DecimalField,
    IntegerField,
    FileField,
    _unset_value
    )
from wtforms.validators import Optional, AnyOf, Length, Email, Regexp
from wtforms.widgets import CheckboxInput, HiddenInput
import  altair.viewhelpers.datetime_
from altair.viewhelpers.datetime_ import create_date_time_formatter, DateTimeHelper
from altair.formhelpers import (
    Translations,
    Max,
    Required, after1900, NFKC, Zenkaku, Katakana, SejCompliantEmail,
    strip_spaces, ignore_space_hyphen, OurForm)
from altair.formhelpers.fields import (
    OurBooleanField,
    OurPHPCompatibleFieldList, 
    DateTimeField,
    DateField, 
    OurSelectField,
    OurSelectMultipleField,
    BugFreeSelectField,
    BugFreeSelectMultipleField,
    OurTextField,
    OurHiddenField,
    OurTextAreaField,
    )
from altair.formhelpers.widgets import (
    OurDateWidget,
    OurDateTimeWidget,
    CheckboxMultipleSelect,
    OurListWidget,
    )
from altair.app.ticketing.core.models import (
    Organization,
    PaymentMethod,
    DeliveryMethod,
    SalesSegmentGroup,
    PaymentDeliveryMethodPair,
    SalesSegment,
    Performance,
    Product,
    ProductItem,
    Event,
    EventSetting,
    Refund,
    PointUseTypeEnum,
    )
from altair.app.ticketing.orders.models import (
    OrderCancelReasonEnum,
    )
from altair.app.ticketing.cart.schemas import ClientForm
from altair.app.ticketing.payments import plugins
from altair.app.ticketing.core import helpers as core_helpers
from altair.app.ticketing.orders.importer import (
    ImportTypeEnum,
    ImportCSVReader,
    AllocationModeEnum,
    )
from altair.app.ticketing.orders.helpers import (
    get_import_type_label,
    get_allocation_mode_label,
    )
from altair.app.ticketing.orders.export import OrderCSV
from altair.app.ticketing.csvutils import AttributeRenderer
from altair.app.ticketing.models import DBSession
from .export import OrderAttributeRenderer
from .models import OrderedProduct, OrderedProductItem
from sqlalchemy import orm

logger = logging.getLogger(__name__)


class ProductsField(Field):
    def __init__(self, _form=None, hide_on_new=False, label=None, validators=None, **kwargs):
        super(ProductsField, self).__init__(label, validators, **kwargs)
        self.form = _form
        self.hide_on_new = hide_on_new

    def _get_translations(self):
        return Translations()

    def process_data(self, data):
        self.data = data

    def process(self, formdata, data=_unset_value):
        self.process_errors = []
        if data is _unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data
        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata:
            self.data = None
            products = {}
            product_items = {}

            for k in formdata:
                v = formdata.getlist(k)[0]
                if k.startswith('product_quantity-'):
                    try:
                        ordered_product_id = long(k[17:])
                    except (TypeError, ValueError) as e:
                        self.process_errors.append(self.gettext(u'invalid parameter name: %s') % k)
                    product = Product.query \
                        .join(OrderedProduct.product) \
                        .join(Product.sales_segment) \
                        .join(SalesSegment.sales_segment_group) \
                        .join(SalesSegmentGroup.event) \
                        .filter(Event.organization_id == self.form.context.organization.id) \
                        .filter(OrderedProduct.id == ordered_product_id) \
                        .first()

                    if product is not None:
                        try:
                            quantity = int(v)
                            products[ordered_product_id] = quantity
                        except (TypeError, ValueError) as e:
                            self.process_errors.append(self.gettext(u'Invalid value for %(field)s') % dict(field=product.name))
                    else:
                        self.process_errors.append(u'商品がありません (id=%d)' % ordered_product_id)

                elif k.startswith('product_item_price-'):
                    try:
                        ordered_product_item_id = long(k[19:])
                    except (TypeError, ValueError) as e:
                        self.process_errors.append(self.gettext(u'invalid parameter name: %s') % k)
                    product_item = ProductItem.query \
                        .join(OrderedProductItem.product_item) \
                        .join(ProductItem.product) \
                        .join(Product.sales_segment) \
                        .join(SalesSegment.sales_segment_group) \
                        .join(SalesSegmentGroup.event) \
                        .filter(Event.organization_id == self.form.context.organization.id) \
                        .filter(OrderedProductItem.id == ordered_product_item_id) \
                        .first()

                    if product_item is not None:
                        try:
                            price = decimal.Decimal(v)
                            product_items[ordered_product_item_id] = price
                        except (TypeError, decimal.InvalidOperation):
                            self.process_errors.append(self.gettext(u'Invalid value for %(field)s') % dict(field=product_item.name))
                    else:
                            self.process_errors.append(u'商品明細がありません (id=%d)' % product_item_id)
                if not self.process_errors:
                    self.data = {
                        'products': products,
                        'product_items': product_items,
                        }

        for filter in self.filters:
            try:
                self.data = filter(self.data)
            except ValueError as e:
                self.process_errors.append(e.args[0])


class OrderInfoForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        # context = kwargs.pop('context')
        #self.context = context
        super(OrderInfoForm, self).__init__(formdata, obj, prefix, **kwargs)

    payment_due_at = DateTimeField(
        label=u'支払期日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateTimeWidget(),
        missing_value_defaults=dict(year='1900', month='1', day='1', hour='0', minute='0', second='59')
    )
    issuing_start_at = DateTimeField(
        label=u'発券開始日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateTimeWidget()
    )
    issuing_end_at = DateTimeField(
        label=u'発券期限日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateTimeWidget(),
        missing_value_defaults=dict(year='1900', month='1', day='1', hour='0', minute='0', second='59')
    )


class RegrantNumberDueAtForm(Form):

    regrant_number_due_at = DateTimeField(
        label=u'再付番用発券期限日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M',
        widget=OurDateTimeWidget(),
        missing_value_defaults=dict(year='1900', month='1', day='1', hour='0', minute='0', second='59')
    )

    def add_error(self, field, error):
        if not hasattr(field.errors, 'append'):
            field.errors = list(field.errors)
            field.errors.append(error)


class OrderForm(Form):

    def _get_translations(self):
        return Translations()

    order_no = HiddenField(
        label=u'予約番号',
        validators=[Optional()],
    )
    total_amount = HiddenField(
        label=u'合計',
        validators=[Optional()],
    )
    created_at = HiddenField(
        label=u'予約日時',
        validators=[Optional(), after1900],
    )
    system_fee = DecimalField(
        label=u'システム利用料',
        places=2,
        default=0,
        validators=[Required()],
    )
    transaction_fee = DecimalField(
        label=u'決済手数料',
        places=2,
        default=0,
        validators=[Required()],
    )
    delivery_fee = DecimalField(
        label=u'引取手数料',
        places=2,
        default=0,
        validators=[Required()],
    )
    special_fee = DecimalField(
        label=u'特別手数料',
        places=2,
        default=0,
        validators=[Required()],
    )
    special_fee_name = TextField(
        label=u'特別手数料名',
        validators=[Optional()],
    )
    products = ProductsField(
        label=u'商品'
        )

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        context = kwargs.pop('context')
        self.context = context
        super(OrderForm, self).__init__(formdata, obj, prefix, **kwargs)

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

        # Eventが指定されていなくて、Performanceが指定される場合のみ、紐づくEventを取る。
        if event is None and performance is not None:
            event = performance.event

        # Organizationが取得されなくて、Eventが取得される場合は、紐づくOrganizationを取る。
        if organization is None and event is not None:
            organization = event.organization

        # organization_id, event_idかperformance_idのいずれがkwagrsにあると、organizationを取得できる。
        if organization:
            self.payment_method.choices = [(pm.id, pm.name) for pm in
                                           PaymentMethod.filter_by_organization_id(organization.id)]
            self.delivery_method.choices = [(dm.id, dm.name) for dm in
                                            DeliveryMethod.filter_by_organization_id(organization.id)]

            # Performanceが指定される場合は該当Performanceのみ表示する。
            if performance:
                self.performance_id.choices = [(performance.id, '%s (%s)' % (
                    performance.name, self.datetime_helper().datetime(performance.start_on, with_weekday=True)))]

            # SalesSegmentGroupが指定される場合は該当SaleSegmentGroupのみ表示する。
            if sales_segment_group:
                self.sales_segment_group_id.choices = [(sales_segment_group.id, sales_segment_group.name)]

            # Eventが指定されていない場合はorgに紐づくEvent一覧をとる。
            if event is None:
                events = Event.query.with_entities(Event.id, Event.title) \
                    .filter(Event.organization_id == organization.id) \
                    .order_by(Event.created_at.desc())
                self.event_id.choices = [('', u'(イベントを選んでください。)')] + [(e.id, e.title) for e in events]
            # Eventが指定される場合は該当Eventのみ表示する。
            else:
                self.event_id.choices = [(event.id, event.title)]
                if not performance:
                    self.performance_id.choices = self.get_performance_choices(self.datetime_helper())
                if not sales_segment_group:
                    self.sales_segment_group_id.choices = self.get_sales_segment_group_choices()

        # POSTされた場合（kwargにevent_idがないため、上のeventを取得できない）の設定
        # Eventが絞られる場合、該当Eventに紐づくPerformanceとsales_segment_groupを取る
        if not event and self.event_id.data:
            self.performance_id.choices = self.get_performance_choices(self.datetime_helper())
            self.sales_segment_group_id.choices = self.get_sales_segment_group_choices()

    def datetime_helper(self):
        return DateTimeHelper(create_date_time_formatter(self.request))

    def get_performance_choices(self, datetime_helper):
        performances = Performance.query.join(Event) \
            .filter(Event.id == self.event_id.data) \
            .order_by(Performance.created_at.desc())
        choices = [('', u'')] + [
            (p.id, '%s (%s)' % (p.name, datetime_helper.datetime(p.start_on, with_weekday=True))) for p in
            performances]
        return choices

    def get_sales_segment_group_choices(self):
        sales_segment_groups = SalesSegmentGroup.query.filter(
            SalesSegmentGroup.event_id == self.event_id.data)
        choices = [(sales_segment_group.id, sales_segment_group.name) for
                   sales_segment_group in sales_segment_groups]
        return choices

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


class OrderRefundIndexSearchForm(SearchFormBase):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(OrderRefundIndexSearchForm, self).__init__(formdata, obj, prefix, **kwargs)

    def _get_translations(self):
        return Translations()

    event_code = TextField(
        label=u'イベントコード',
        validators=[Optional()],
    )

    performance_code = TextField(
        label=u'パフォーマンスコード',
        validators=[Optional()],
    )


class OrderRefundSearchForm(OrderSearchForm):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(OrderRefundSearchForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.status.data = list(self.status.data or ()) + ['ordered', 'delivered']
        self.payment_status.data = ['paid']
        self.public.data = u'一般発売のみ'

        # すべては選択不可
        self.event_id.choices.pop(0)

    def _get_translations(self):
        return Translations()

    payment_method = SelectField(
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
    event_id = SelectField(
        label=u"イベント",
        coerce=lambda x : int(x) if x else u"",
        choices=[],
        validators=[Required()],
    )
    performance_id = SelectMultipleField(
        label=u"公演",
        coerce=lambda x : int(x) if x else u"",
        choices=[],
        validators=[Required()],
    )
    sales_segment_group_id = SelectMultipleField(
        label=u'販売区分',
        coerce=lambda x : int(x) if x else u"",
        choices=[],
        validators=[Optional()],
    )
    status = BugFreeSelectMultipleField(
        label=u'ステータス',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Required()],
        choices=[
            ('ordered', u'受付済み'),
            ('delivered', u'配送済み'),
        ],
        coerce=str,
    )
    payment_status = BugFreeSelectMultipleField(
        label=u'決済ステータス',
        widget=CheckboxMultipleSelect(multiple=True),
        validators=[Required()],
        choices=[
            ('paid', u'入金済み'),
        ],
        coerce=str,
    )
    public = TextField(
        label=u'一般発売',
        validators=[Optional()],
    )

    def validate(self):
        status = super(type(self), self).validate()
        if status:
            # 決済方法か引取方法のいずれかは必須
            if not self.payment_method.data and not self.delivery_method.data:
                self.payment_method.errors.append(u'決済方法か引取方法のいずれかを選択してください')
                status = False
        return status

class PerformanceSearchForm(Form):
    event_id = HiddenField(
        validators=[Optional()],
    )
    sort = HiddenField(
        validators=[Optional()],
        default='id'
    )
    direction = HiddenField(
        validators=[Optional(), AnyOf(['asc', 'desc'], message='')],
        default='desc',
    )
    public = HiddenField(
        validators=[Optional()],
    )
    performance_opt_all_disable = BooleanField(
        validators=[Optional()],
    )


class SalesSegmentGroupSearchForm(Form):
    event_id = HiddenField(
        validators=[Optional()],
    )
    sort = HiddenField(
        validators=[Optional()],
        default='id'
    )
    direction = HiddenField(
        validators=[Optional(), AnyOf(['asc', 'desc'], message='')],
        default='desc',
    )
    public = HiddenField(
        validators=[Optional()],
    )


class OrderReservePreconditionsForm(OurForm):
    performance_id = OurHiddenField(
        label=u'公演',
        validators=[Required()]
        )
    stocks = OurPHPCompatibleFieldList(
        OurHiddenField(),
        widget=OurListWidget(
            outer_html_tag=None,
            inner_html_tag=None,
            omit_labels=True
            )
        )

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        self.context = context
        super(OrderReservePreconditionsForm, self).__init__(*args, **kwargs)


class OrderReserveSalesSegmentChooserForm(OurForm):
    sales_segment_id = OurSelectField(
        label=u'販売区分',
        validators=[Optional()],
        choices=lambda field: [(None, u'(すべて)')] + [
            (sales_segment.id, u'%s %s' % (sales_segment.name, DateTimeHelper(create_date_time_formatter(field.form.context.request)).term(sales_segment.start_at, sales_segment.end_at)))
            for sales_segment in field.form.context.sales_segments
            ],
        encoder=lambda x : u'' if x is None else u'%d' % x,
        coerce=lambda x : int(x) if x else None
        )

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        self.context = context
        super(OrderReserveSalesSegmentChooserForm, self).__init__(*args, **kwargs)


class OrderReserveSettingsForm(OurForm):
    sales_segment_id = OurSelectField(
        label=u'販売区分',
        validators=[Required()],
        choices=lambda field: [
            (sales_segment.id, u'%s %s' % (sales_segment.name, DateTimeHelper(create_date_time_formatter(field.form.context.request)).term(sales_segment.start_at, sales_segment.end_at)))
            for sales_segment in field.form.context.sales_segments
            ],
        encoder=lambda x : u'' if x is None else u'%d' % x,
        coerce=lambda x : int(x) if x else None
        )

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        self.context = context
        super(OrderReserveSettingsForm, self).__init__(*args, **kwargs)


class OrderReserveSeatsForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        self.context = kwargs.pop('context', None)
        super(OrderReserveSeatsForm, self).__init__(formdata, obj, prefix, **kwargs)

    seats = OurPHPCompatibleFieldList(
        OurHiddenField(),
        widget=OurListWidget(
            outer_html_tag=None,
            inner_html_tag=None,
            omit_labels=True
            )
        )


class OrderReserveForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        self.context = kwargs.pop('context', None)
        super(OrderReserveForm, self).__init__(formdata, obj, prefix, **kwargs)

    def _get_translations(self):
        return Translations()

    def get_defalut_sales_counter_payment_method(self):
        for (pm_id, label) in self.sales_counter_payment_method_id.choices:
            pm = PaymentMethod.query.filter_by(id=pm_id).first()
            if pm and pm.payment_plugin_id == plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID:
                return pm_id
        return 0

    note = OurTextAreaField(
        label=u'備考・メモ',
        validators=[
            Optional(),
            Length(max=2000, message=u'2000文字以内で入力してください'),
            ]
        )
    products = OurSelectMultipleField(
        label=u'商品',
        validators=[Optional()],
        choices=lambda field: [(product.id, product.name) for product in field.form.context.products],
        coerce=int
        )
    payment_delivery_method_pair_id = OurSelectField(
        label=u'決済・引取方法',
        validators=[Required(u'決済・引取方法を選択してください')],
        choices=lambda field: \
            [
                (
                    payment_delivery_method_pair.id,
                    '%s  -  %s' % (payment_delivery_method_pair.payment_method.name, payment_delivery_method_pair.delivery_method.name)
                    )
                for payment_delivery_method_pair in field.form.context.payment_delivery_method_pairs
                ],
        coerce=lambda x : int(x) if x else u'',
        )
    sales_counter_payment_method_id = OurSelectField(
        label=u'当日窓口決済',
        validators=[Optional()],
        choices=lambda field: list(
            itertools.chain(
                [(0, '')],
                (
                    (pm.id, pm.name)
                    for pm in DBSession.query(PaymentMethod).filter(PaymentMethod.organization_id == field.form.context.organization.id)
                    )
                )
            ),
        coerce=int
        )
    last_name = OurTextField(
        label=u'姓',
        filters=[strip_spaces],
        validators=[
            Optional(),
            Zenkaku,
            Length(max=10, message=u'10文字以内で入力してください'),
            ]
        )
    last_name_kana = OurTextField(
        label=u'姓(カナ)',
        filters=[strip_spaces, NFKC],
        validators=[
            Optional(),
            Katakana,
            Length(max=10, message=u'10文字以内で入力してください'),
            ]
        )
    first_name = OurTextField(
        label=u'名',
        filters=[strip_spaces],
        validators=[
            Optional(),
            Zenkaku,
            Length(max=10, message=u'10文字以内で入力してください'),
            ]
        )
    first_name_kana = OurTextField(
        label=u'名(カナ)',
        filters=[strip_spaces, NFKC],
        validators=[
            Optional(),
            Katakana,
            Length(max=10, message=u'10文字以内で入力してください'),
            ]
        )
    zip = OurTextField(
        label=u'郵便番号',
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=7, max=7),
            Regexp(r'^\d{7}$', message=u'-(ハイフン)を抜いた半角数字のみを入力してください')
        ]
    )
    prefecture = OurTextField(
        label=u"都道府県",
        filters=[strip_spaces],
        validators=[
            Optional(),
        ]
    )
    city = OurTextField(
        label=u"市区町村",
        filters=[strip_spaces],
        validators=[
            Optional(),
        ]
    )
    address_1 = OurTextField(
        label=u"町名番地",
        filters=[strip_spaces],
        validators=[
            Optional(),
        ]
    )
    address_2 = OurTextField(
        label=u"建物名等",
        filters=[strip_spaces],
        validators=[
            Optional(),
        ]
    )
    email_1 = OurTextField(
        label=u"メールアドレス",
        filters=[strip_spaces, NFKC],
        validators=[
            Optional(),
            SejCompliantEmail()
        ]
    )
    tel_1 = OurTextField(
        label=u'TEL',
        filters=[ignore_space_hyphen],
        validators=[
            Optional(),
            Length(min=10, max=11),
            Regexp(r'^\d*$', message=u'-(ハイフン)を抜いた半角数字のみを入力してください'),
        ]
    )

    def validate_payment_delivery_method_pair_id(form, field):
        if field.data:
            try:
                pdmp = DBSession.query(PaymentDeliveryMethodPair).filter_by(id=field.data).one()
            except (NoResultFound, MultipleResultsFound):
                raise ValidationError(u'選択された決済引取方法に不備があり、決済引取方法の設定をご確認ください。')

            if any(True for payment_delivery_method_pair in form.context.convenience_payment_delivery_method_pairs if field.data == payment_delivery_method_pair.id):
                for field_name in ['last_name', 'first_name', 'last_name_kana', 'first_name_kana', 'tel_1']:
                    f = getattr(form, field_name)
                    if not f.data:
                        err_msg = u'{}を入力してください'.format(f.label.text)
                        raise ValidationError(err_msg)

                # 決済せずにコンビニ受取できるのはadministratorのみ (不正行為対策)
                if (not pdmp.payment_method.pay_at_store() and pdmp.delivery_method.deliver_at_store()) \
                    and not form.context._is_event_editor:
                        raise ValidationError(u'この決済引取方法を選択する権限がありません')

            # 楽天ペイで予約タブから予約を取れないようにする
            if pdmp.payment_method.payment_plugin_id == plugins.CHECKOUT_PAYMENT_PLUGIN_ID:
                raise ValidationError(u'予約タブで楽天ペイは使えません')


class OrderRefundForm(OurForm):

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        super(type(self), self).__init__(*args, **kwargs)
        self.context = context
        payment_methods = PaymentMethod.filter_by_organization_id(context.organization.id)
        self.payment_method_id.choices = [(int(pm.id), pm.name) for pm in payment_methods]
        self.orders = kwargs.get('orders', [])

    def _get_translations(self):
        return Translations()

    @property
    def convenience_payment_method_ids(self):
        payment_method_ids = []
        payment_methods = PaymentMethod.filter_by_organization_id(self.context.organization.id)
        for pm in payment_methods:
            if pm.payment_plugin_id in (plugins.SEJ_PAYMENT_PLUGIN_ID, plugins.FAMIPORT_PAYMENT_PLUGIN_ID):
                payment_method_ids.append(pm.id)
        return payment_method_ids

    payment_method_id = SelectField(
        label=u'払戻方法',
        validators=[Required()],
        choices=[],
        coerce=int,
    )
    include_item = IntegerField(
        label=u'商品金額',
        validators=[Optional()],
        default=0,
        widget=CheckboxInput(),
    )
    include_system_fee = IntegerField(
        label=u'システム利用料',
        validators=[Optional()],
        default=0,
        widget=CheckboxInput(),
    )
    include_special_fee = IntegerField(
        label=u'特別手数料',
        validators=[Optional()],
        default=0,
        widget=CheckboxInput(),
    )
    include_transaction_fee = IntegerField(
        label=u'決済手数料',
        validators=[Optional()],
        default=0,
        widget=CheckboxInput(),
    )
    include_delivery_fee = IntegerField(
        label=u'引取手数料',
        validators=[Optional()],
        default=0,
        widget=CheckboxInput(),
    )
    cancel_reason = SelectField(
        label=u'キャンセル理由',
        validators=[Required()],
        choices=[e.v for e in OrderCancelReasonEnum],
        coerce=int
    )
    start_at = DateTimeField(
        label=u'払戻期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d',
        widget=OurDateTimeWidget()
    )
    end_at = DateTimeField(
        label=u'払戻期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max,
        ),
        widget=OurDateTimeWidget()
    )
    need_stub = OurSelectField(
        label=u'半券要否区分',
        help=u'コンビニ店頭での払戻の際に、半券があるチケットのみ有効とするかどうかを指定します。' +
             u'<br>公演前のケースでは「要」を指定、公演途中での中止等のケースでは「不要」を指定してください。',
        choices=[(1, u'要'), (0, u'不要')],
        validators=[Optional()],
        coerce=int,
    )
    id = HiddenField(
        validators=[Optional()],
    )

    def validate_payment_method_id(form, field):
        refund_pm = PaymentMethod.get(field.data)
        error_msg = u'指定された払戻方法は、この決済引取方法では選択できません'
        for refund_order in form.orders:
            settlement_payment_plugin_id = refund_order.payment_delivery_pair.payment_method.payment_plugin_id
            settlement_delivery_plugin_id = refund_order.payment_delivery_pair.delivery_method.delivery_plugin_id

            if refund_pm.can_use_point() and refund_order.point_use_type is PointUseTypeEnum.AllUse:
                # TKT-6643 払戻方法にポイント利用可能な支払方法が選択され、かつ全額ポイント払いの場合は以降のバリデーションをスキップ
                # ポイント利用可能な支払方法を判定する理由は、このバリデーションを通過してポイント利用を考慮していない決済プラグインの
                # refund_orderを実行させたくないため。つまり影響範囲を最小とするため。
                continue

            # コンビニ引取
            if settlement_delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID:
                # コンビニ跨ぎは出来ない
                if refund_pm.payment_plugin_id == plugins.FAMIPORT_PAYMENT_PLUGIN_ID:
                    raise ValidationError('%s: %s(%s)' % (error_msg, u'セブン発券のチケットはファミマ払戻は出来ません', refund_order.order_no))
                if refund_order.is_issued():
                    # 発券済ならコンビニ払戻のみ可能
                    if refund_pm.payment_plugin_id != plugins.SEJ_PAYMENT_PLUGIN_ID:
                        raise ValidationError('%s: %s(%s)' % (error_msg, u'既にコンビニ発券済なのでコンビニ払戻(セブン)を選択してください', refund_order.order_no))
            elif settlement_delivery_plugin_id == plugins.FAMIPORT_DELIVERY_PLUGIN_ID:
                # コンビニ跨ぎは出来ない
                if refund_pm.payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID:
                    raise ValidationError('%s: %s(%s)' % (error_msg, u'ファミマ発券のチケットはセブン払戻は出来ません', refund_order.order_no))
                if refund_order.is_issued():
                    # 発券済ならコンビニ払戻のみ可能
                    if refund_pm.payment_plugin_id != plugins.FAMIPORT_PAYMENT_PLUGIN_ID:
                        raise ValidationError('%s: %s(%s)' % (error_msg, u'既にコンビニ発券済なのでコンビニ払戻(ファミマ)を選択してください', refund_order.order_no))
            elif refund_pm.payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID or refund_pm.payment_plugin_id == plugins.FAMIPORT_PAYMENT_PLUGIN_ID:
                # コンビニ引取でないならコンビニ払戻は不可
                raise ValidationError('%s: %s(%s)' % (error_msg, u'コンビニ引取ではありません', refund_order.order_no))

            # 決済方法=払戻方法 または払戻方法がコンビニ払戻/銀行振込ならOK
            if refund_pm.payment_plugin_id not in [settlement_payment_plugin_id, plugins.SEJ_PAYMENT_PLUGIN_ID, plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID, plugins.FAMIPORT_PAYMENT_PLUGIN_ID]:
                raise ValidationError('%s: (%s)' % (error_msg, refund_order.order_no))

    def validate(self):
        status = super(type(self), self).validate()
        if status:
            if not self.include_item.data and \
               not self.include_system_fee.data and \
               not self.include_special_fee.data and \
               not self.include_transaction_fee.data and \
               not self.include_delivery_fee.data:
                self.include_item.errors.append(u'払戻対象を選択してください')
                status = False

            # コンビニ払戻なら必須
            refund_pm = PaymentMethod.get(self.payment_method_id.data)
            if refund_pm.payment_plugin_id in [plugins.SEJ_PAYMENT_PLUGIN_ID, plugins.FAMIPORT_PAYMENT_PLUGIN_ID]:
                if not self.start_at.data:
                    self.start_at.errors.append(u'入力してください')
                    status = False
                if not self.end_at.data:
                    self.end_at.errors.append(u'入力してください')
                    status = False
                if self.start_at.data and self.end_at.data and self.start_at.data > self.end_at.data:
                    self.end_at.errors.append(u'開始日よりも後に終了日が設定されています')
                    status = False
            if refund_pm.payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID:
                if self.need_stub.data is None:
                    self.need_stub.errors.append(u'コンビニ払戻の場合は半券要否区分を選択してください')
                    status = False

            # 払戻予約ステータスのみ変更可能
            if self.id.data:
                refund = Refund.get(self.id.data)
                if not refund.editable():
                    self.id.errors.append(u'払戻中または払戻済の為、変更できません')
                    status = False

        return status


class OrderImportForm(OurForm):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        if 'ignore_columns' in kwargs:
            self.ignore_columns = kwargs.get('ignore_columns')

    def _get_translations(self):
        return Translations()

    order_csv = FileField(
        u'CSVファイル',
        validators=[]
    )
    import_type = BugFreeSelectField(
        label=u'インポート方法',
        validators=[Required()],
        choices=[(str(e.v), get_import_type_label(e.v)) for e in ImportTypeEnum],
        default=ImportTypeEnum.Update.v,
        coerce=int,
    )
    enable_random_import = OurBooleanField(
        label=u'ランダムインポート'
    )
    allocation_mode = BugFreeSelectField(
        label=u'配席モード',
        validators=[Required()],
        choices=[(str(e.v), get_allocation_mode_label(e.v)) for e in AllocationModeEnum],
        default=AllocationModeEnum.AlwaysAllocateNew.v,
        coerce=int,
    )
    merge_order_attributes = OurBooleanField(
        label=u'既存の予約の購入情報属性を更新する',
        help=u'チェックを入れずに実行すると、属性はCSVに書かれているものに置換となりますので注意してください',
        default=True
    )
    use_test_version = OurBooleanField(
        label=u'テスト版を使う'
    )

    def validate_order_csv(form, field):
        if not hasattr(field.data, 'file'):
            raise ValidationError(u'選択してください')

        if len(field.data.file.readlines()) < 2:
            raise ValidationError(u'データがありません')
        field.data.file.seek(0)

        # ヘッダーをチェック
        try:
            reader = ImportCSVReader(field.data.file, encoding='cp932:normalized-tilde')
        except csv.Error as e:
            raise ValidationError(u"ファイルはCSVで指定してください。または、CSV処理中にエラーが発生しました。{}".format(e.message))
        import_header = reader.fieldnames
        field.data.file.seek(0)

        # 「,,,,,,,,,,,,,,...」の行をチェック
        is_blank_line = False

        for row in reader:
            is_blank_line = True
            for k, v in row.iteritems():
                if v is not None and v != u'':
                    is_blank_line = False
            if is_blank_line:
                break

        if is_blank_line:
            raise ValidationError(u'ファイル内に空の行が入っています')
        field.data.file.seek(0)

        export_header = []
        attribute_renderers = []
        for c in OrderCSV.per_seat_columns:
            if not isinstance(c, (AttributeRenderer, OrderAttributeRenderer)):
                if hasattr(c, 'column_name'):
                    column_name = c.column_name
                else:
                    column_name = c.key
                export_header.append(column_name)
            else:
                attribute_renderers.append(c)

        for h in import_header:
            for c in attribute_renderers:
                g = re.match(u'%s\[([^]]*)\]' % c.variable_name, h)
                if g is not None:
                    export_header.append(h)

        difference = set(import_header) - set(export_header) - set(form.ignore_columns)
        if len(difference) > 0 or len(import_header) == 0:
            raise ValidationError(u'CSVファイルのフォーマットが正しくありません (不明なカラム: %s)' % u', '.join(unicode(s) for s in difference))


class ClientOptionalForm(ClientForm):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        ClientForm.__init__(self, formdata, obj, prefix, **kwargs)

        # 全てのフィールドをOptionalにする
        for field in self:
            for i, validator in enumerate(field.validators):
                setattr(field.flags, 'required', False)
                if isinstance(validator, Required):
                    del field.validators[i]
                    break;
            field.validators.append(Optional())

    def _validate_tel_1(self, *args, **kwargs):
        # 電話番号1の validation をしない (ClientForm._validate_tel_1 をオーバライド)
        return True

    def _validate_email_addresses(self, *args, **kwargs):
        # メールアドレスの validation をしない (ClientForm._validate_email_addresses をオーバライド)
        return True

class SejTicketForm(Form):
    ticket_type = SelectField(
        label=u'チケット区分',
        choices=[(u'', '-'),(u'1', u'本券（バーコード付き）'), (u'2', u'本券'), (u'3', u' 副券（バーコード付き）'), (u'4', u' 副券')],
        validators=[Optional()],
    )
    event_name              = TextField(
        label=u'イベント名',
        validators=[Required()],
    )
    performance_name        = TextField(
        label=u'パフォーマンス名',
        validators=[Required()],
    )
    performance_datetime    = DateTimeField(
        label=u'発券期限',
        validators=[Optional(), after1900],
    )
    ticket_template_id      = TextField(
        label=u'テンプレートID',
        validators=[Required()],
    )
    ticket_data_xml         = TextAreaField(
        label=u'XML',
        validators=[Required()],
    )

class SejOrderForm(Form):
    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    order_no= TextField(
        label=u'オーダーID',
        validators=[Optional()],
    )
    shop_id= TextField(
        label=u'ショップID',
        default=30520,
        validators=[Optional()],
    )
    shop_name= TextField(
        label=u'ショップ名',
        default=u'楽天チケット',
        validators=[Optional()],
    )
    contact_01= TextField(
        label=u'連絡先１',
        validators=[Optional()],
    )
    contact_02= TextField(
        label=u'連絡先２',
        validators=[Optional()],
    )
    user_name= TextField(
        label=u'ユーザー名',
        validators=[Optional()],
    )
    user_name_kana= TextField(
        label=u'ユーザー名（カナ）',
        validators=[Optional()],
    )
    tel= TextField(
        label=u'ユーザー電話番号',
        validators=[Optional()],
    )
    zip_code= TextField(
        label=u'ユーザー郵便番号',
        validators=[Optional()],
    )
    email= TextField(
        label=u'ユーザーEmail',
        validators=[Optional()],
    )

    total_price = TextField(
        label=u'合計',
        validators=[Required()],
    )
    ticket_price = TextField(
        label=u'チケット金額',
        validators=[Required()],
    )
    commission_fee = TextField(
        label=u'手数料',
        validators=[Required()],
    )
    ticketing_fee = TextField(
        label=u'発券手数料',
        validators=[Required()],
    )

    payment_due_at = DateTimeField(
        label=u'支払い期限',
        validators=[Optional(), after1900],
    )
    ticketing_start_at = DateTimeField(
        label=u'発券開始',
        validators=[Optional(), after1900],
    )
    ticketing_due_at = DateTimeField(
        label=u'発券期限',
        validators=[Optional(), after1900],
    )
    regrant_number_due_at = DateTimeField(
        label=u'SVC再付番期限',
        validators=[Required(), after1900],
    )

    payment_type = SelectField(
        label=u'支払い方法',
        choices=[(u'1', u'代引き'), (u'2', u'前払い(後日発券)'), (u'3', u' 代済発券'), (u'4', u' 前払いのみ')],
        validators=[Optional()],
    )

    update_reason = SelectField(
        label=u'更新理由',
        choices=[(u'1', u'項目変更'), (u'2', u'公演中止')],
        validators=[Optional()],
    )


class SejRefundEventForm(OurForm):

    available = OurBooleanField(
        label=u'有効フラグ',
        validators=[Required()],
    )
    shop_id = TextField(
        label=u'ショップID',
        default=30520,
        validators=[Required()],
    )
    event_code_01      = TextField(
        label=u'公演決定キー1	',
        validators=[Required()],
    )
    event_code_02       = TextField(
        label=u'公演決定キー2	',
        validators=[Optional()],
    )
    title      = TextField(
        label=u'メインタイトル',
        validators=[Required()],
    )
    sub_title      = TextField(
        label=u'サブタイトル',
        validators=[Optional()],
    )
    event_at = DateTimeField(
        label=u'公演日',
        validators=[Required(), after1900],
    )
    start_at = DateTimeField(
        label=u'レジ払戻受付開始日	',
        validators=[Required(), after1900],
    )
    end_at = DateTimeField(
        label=u'レジ払戻受付終了日	',
        validators=[Required(), after1900],
    )
    event_expire_at = DateTimeField(
        label=u'公演レコード有効期限	',
        validators=[Required(), after1900],
    )
    ticket_expire_at = DateTimeField(
        label=u'チケット持ち込み期限	',
        validators=[Required(), after1900],
    )
    refund_enabled = OurBooleanField(
        label=u'レジ払戻可能フラグ',
        validators=[Required()],
    )
    disapproval_reason  = TextField(
        label=u'払戻不可理由',
        validators=[Optional()],
    )
    need_stub = RadioField(
        label=u'半券要否区分',
        choices=[(u'0', u'不要'), (u'1', u'要')],
        validators=[Required()],
    )
    remarks  = TextField(
        label=u'備考',
        validators=[Optional()],
    )

def cancel_events():
    from altair.app.ticketing.sej.models import SejRefundEvent
    return SejRefundEvent.all()

from wtforms.ext.sqlalchemy.fields import QuerySelectField,QuerySelectMultipleField


class SejRefundOrderForm(Form):

    event = QuerySelectField(label=u'払戻対象イベント',get_label=lambda x: u'%d:%s(%s)' % (x.id, x.title, x.sub_title), query_factory=cancel_events, allow_blank=False)
    refund_ticket_amount      = TextField(
        label=u'払戻チケット代金',
        validators=[Optional()],
    )
    refund_other_amount      = TextField(
        label=u'その他払戻金額',
        validators=[Optional()],
    )

class SendingMailForm(Form):
    # subject = TextField(
    #     label=u"メールタイトル",
    #     validators=[
    #         Required(),
    #     ]
    # )
    recipient = TextField(
        label=u"送り先メールアドレス",
        validators=[
            Required(),
            Email(),
        ]
    )
    bcc = TextField(
        label=u"bcc",
        validators=[
            Email(),
            Optional()
        ]
    )

class TicketFormatSelectionForm(OurForm):
    ticket_format_id = BugFreeSelectField(
        label=u"チケット様式",
        choices=[],
        coerce=long,
        validators=[Optional()],
    )

    def __init__(self, *args, **kwargs):
        context = kwargs.pop('context')
        super(TicketFormatSelectionForm, self).__init__(*args, **kwargs)
        self.context = context
        available_ticket_formats = context.available_ticket_formats
        self.ticket_format_id.choices = [(unicode(t.id),  t.name) for t in available_ticket_formats]

        if self.ticket_format_id.data is None and self.context.default_ticket_format is not None:
            self.ticket_format_id.data = self.context.default_ticket_format.id


class CheckedOrderTicketChoiceForm(Form):
    ticket_format_id = SelectField(
        label=u"チケット様式",
        coerce=int,
        choices=[],
    )

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        ticket_formats = kwargs.get('ticket_formats')
        if ticket_formats:
            self.ticket_format_id.choices = [(t.id,  t.name) for t in ticket_formats]

class CartSearchForm(SearchFormBase):
    carted_from = DateTimeField(
        label=u'カート生成日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M:%S',
        widget=OurDateTimeWidget()
    )
    carted_to = DateTimeField(
        label=u'カート生成日時',
        validators=[Optional(), after1900],
        format='%Y-%m-%d %H:%M:%S',
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
    browserid = TextField(
        label=u'browserid',
        validators=[Optional()]
        )
    status = SelectField(
        label=u'状態',
        validators=[Optional()],
        choices=[
            ('', u'すべて'),
            ('completed', u'注文成立'),
            ('incomplete', u'注文不成立'),
        ]
    )

def OrderMemoEditFormFactory(N, memo_field_name_fmt="memo_on_order{}",
                                   memo_field_label_fmt=u"補助文言{}(最大20文字)"):
    attrs = {}
    for i in range(1, N+1):
        name = memo_field_name_fmt.format(i)
        label = memo_field_label_fmt.format(i)
        attrs[name] = TextField(label=label, validators=[Optional(), Length(max=20)])#todo: 全角20文字

    def get_error_messages(self):
        messages = []
        for field in self:
            mes = u"{}:{}".format(field.label.text, u", ".join(field.errors))
            messages.append(mes)
        return u"\n".join(messages)
    attrs["get_error_messages"] = get_error_messages

    def get_result(self):
        result = []
        for field in self:
            result.append((field.name, field.data))
        return result
    attrs["get_result"] = get_result
    return type("OrderMemoEditForm", (Form, ), attrs)


class DeliverdEditForm(OurForm):
    delivered_at = DateTimeField(
        label=u'配送日時',
        validators=[Required(message=u"配送時刻が指定されていません"), after1900],
        format='%Y-%m-%d %H:%M',
    )


class CancelForm(OurForm):
    validated = HiddenField(
        label=u'バリデート済フラグ',
        validators=[Optional()],
    )
    order_no = TextField(
        label=u"予約番号",
        validators=[
            Required(),
        ]
    )


class SejOrderCancelForm(CancelForm):

    def validate(self, *args, **kwargs):
        err = None
        order = None
        if len(args):
            order = args[0].pop('order', None)

        if not order:
            err = ValidationError(u"予約が見つかりません")

        if order:
            if order.payment_delivery_method_pair.delivery_method.delivery_plugin_id != plugins.SEJ_DELIVERY_PLUGIN_ID \
                    and order.payment_delivery_method_pair.payment_method.payment_plugin_id != plugins.SEJ_PAYMENT_PLUGIN_ID:
                    err = ValidationError(u"セブン-イレブンの予約ではありません")

            if order.status == 'canceled':
                err = ValidationError(u"既にキャンセルされています。")

            if order.status == 'refunded':
                err = ValidationError(u"払戻されている予約になります。")

        if err:
            if not hasattr(self.order_no.errors, 'append'):
                self.order_no.errors = list(self.order_no.errors)
            self.order_no.errors.append(err)
            return False
        return True


class FamiPortOrderCancelForm(CancelForm):

    def validate(self, *args, **kwargs):
        err = None
        order = None
        if len(args):
            order = args[0].pop('order', None)

        if not order:
            err = ValidationError(u"予約が見つかりません")

        if order:
            if order.payment_delivery_method_pair.delivery_method.delivery_plugin_id != plugins.FAMIPORT_DELIVERY_PLUGIN_ID \
                    and order.payment_delivery_method_pair.payment_method.payment_plugin_id != plugins.FAMIPORT_PAYMENT_PLUGIN_ID:
                    err = ValidationError(u"ファミマの予約ではありません")

            if order.status == 'canceled':
                err = ValidationError(u"既にキャンセルされています。")

            if order.status == 'refunded':
                err = ValidationError(u"払戻されている予約になります。")

        if err:
            if not hasattr(self.order_no.errors, 'append'):
                self.order_no.errors = list(self.order_no.errors)
            self.order_no.errors.append(err)
            return False
        return True


class DownloadItemsPatternForm(OurForm):
    organization_id = HiddenField(
        validators=[Required()]
    )
    pattern_name = OurTextField(
        label=u'',
        validators=[Required()]
    )
    pattern_content = OurTextField(
        label=u'',
        validators=[Required()]
    )