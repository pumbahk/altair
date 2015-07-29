# -*- coding: utf-8 -*-

import logging
import re
from pyramid.security import has_permission, ACLAllowed
from paste.util.multidict import MultiDict
import decimal
from wtforms import Form, ValidationError
from wtforms.fields import (
    Field,
    HiddenField,
    TextField,
    SelectField,
    SelectMultipleField,
    TextAreaField,
    RadioField,
    FieldList,
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
    DateTimeField, DateField, Max, OurDateWidget, OurDateTimeWidget, OurSelectField,
    CheckboxMultipleSelect, BugFreeSelectField, BugFreeSelectMultipleField,
    Required, after1900, NFKC, Zenkaku, Katakana,
    strip_spaces, ignore_space_hyphen, OurForm)
from altair.formhelpers.fields import (
    OurBooleanField,
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
    Refund
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
        widget=OurDateTimeWidget()
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
        widget=OurDateTimeWidget()
    )


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

        if event is None and performance is not None:
            event = performance.event

        if organization is None and event is not None:
            organization = event.organization

        if organization is not None:
            self.payment_method.choices = [(pm.id, pm.name) for pm in PaymentMethod.filter_by_organization_id(organization.id)]
            self.delivery_method.choices = [(dm.id, dm.name) for dm in DeliveryMethod.filter_by_organization_id(organization.id)]
            if event is None:
                events = Event.query.join(Event.setting) \
                                    .filter(Event.organization_id==organization.id) \
                                    .filter(EventSetting.visible==True) \
                                    .order_by(Event.created_at.desc())
                self.event_id.choices = [('', u'(すべて)')]+[(e.id, e.title) for e in events]
            else:
                self.event_id.choices = [(event.id, event.title)]

        # Event が指定されていなかったらフォームから取得を試みる
        if event is None and self.event_id.data:
            event = Event.get(self.event_id.data)

        dthelper = DateTimeHelper(create_date_time_formatter(self.request))
        if event is not None:
            if performance is None:
                performances = Performance.filter_by(event_id=event.id)
                self.performance_id.choices = [
                    ('', u'(すべて)')]+[(p.id, '%s (%s)' % (p.name, dthelper.datetime(p.start_on, with_weekday=True))) for p in performances]
            else:
                self.performance_id.choices = [(performance.id, '%s (%s)' % (performance.name, dthelper.datetime(performance.start_on, with_weekday=True)))]
            if sales_segment_group is None:
                sales_segment_groups = SalesSegmentGroup.query.filter(SalesSegmentGroup.event_id == event.id)
                self.sales_segment_group_id.choices = [(sales_segment_group.id, sales_segment_group.name) for sales_segment_group in sales_segment_groups]
            else:
                self.sales_segment_group_id.choices = [(sales_segment_group.id, sales_segment_group.name)]
        else:
            if organization is not None:
                performances = Performance.query.join(Event) \
                                                .join(Event.setting) \
                                                .filter(Event.organization_id == organization.id) \
                                                .filter(EventSetting.visible == True) \
                                                .order_by(Event.created_at.desc())
            else:
                performances = Performance.query
            self.performance_id.choices = [('', u'(すべて)')] + [(p.id, '%s (%s)' % (p.name, dthelper.datetime(p.start_on, with_weekday=True))) for p in performances]

        # Performance が指定されていなかったらフォームから取得を試みる
        if performance is None and self.performance_id.data:
            if not isinstance(self.performance_id.data, list):
                performance = Performance.get(self.performance_id.data)

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
        format='%Y-%m-%d',
        widget=OurDateWidget()
    )
    start_on_to = DateTimeField(
        label=u'公演日',
        validators=[Optional(), after1900],
        format='%Y-%m-%d',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max,
            hour=Max,
            minute=Max,
            second=Max,
            ),
        widget=OurDateWidget()
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
    billing_or_exchange_number = TextField(
        label=u'セブン−イレブン払込票/引換票番号',
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

class OrderRefundSearchForm(OrderSearchForm):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(OrderRefundSearchForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.status.data = list(self.status.data or ()) + ['ordered', 'delivered']
        self.payment_status.data = ['paid']
        self.public.data = u'一般発売のみ'

        # すべては選択不可
        self.event_id.choices.pop(0)
        self.performance_id.choices.pop(0)

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


class OrderReserveForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(OrderReserveForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.request = kwargs.pop('request', None)

        if 'performance_id' in kwargs:
            performance = Performance.get(kwargs['performance_id'])
            self.performance_id.data = performance.id

            query = Product.query.filter(Product.performance_id==performance.id)
            if 'stocks' in kwargs and kwargs['stocks']:
                query = query.join(ProductItem).filter(ProductItem.stock_id.in_(kwargs['stocks']))

            sales_segments = set(product.sales_segment for product in query.distinct())

            self.sales_segment_id.choices = [
                (sales_segment.id, u'%s %s' % (sales_segment.name, DateTimeHelper(create_date_time_formatter(self.request)).term(sales_segment.start_at, sales_segment.end_at)))
                for sales_segment in \
                    core_helpers.build_sales_segment_list_for_inner_sales(sales_segments, request=self.request)
                ]

            if 'sales_segment_id' in kwargs and kwargs['sales_segment_id']:
                self.sales_segment_id.default = kwargs['sales_segment_id']
            elif len(self.sales_segment_id.choices) > 0:
                self.sales_segment_id.default = self.sales_segment_id.choices[0][0]

            self.products.choices = []
            if 'stocks' in kwargs and kwargs['stocks']:
                query = query.filter(Product.sales_segment_id==self.sales_segment_id.default)
                for p in query.all():
                    self.products.choices += [(p.id, p)]

            self.payment_delivery_method_pair_id.choices = []
            self.payment_delivery_method_pair_id.sej_plugin_id = []
            sales_segment = SalesSegment.get(self.sales_segment_id.default)
            pdmps = sorted(
                sales_segment.payment_delivery_method_pairs,
                key=lambda x: (x.payment_method.payment_plugin_id == plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID),
                reverse=True
            )
            for pdmp in pdmps:
                self.payment_delivery_method_pair_id.choices.append(
                    (pdmp.id, '%s  -  %s' % (pdmp.payment_method.name, pdmp.delivery_method.name))
                )
                if pdmp.payment_method.payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID or \
                   pdmp.delivery_method.delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID:
                    self.payment_delivery_method_pair_id.sej_plugin_id.append(int(pdmp.id))

            self.sales_counter_payment_method_id.choices = [(0, '')]
            for pm in PaymentMethod.filter_by_organization_id(performance.event.organization_id):
                self.sales_counter_payment_method_id.choices.append((pm.id, pm.name))

    def _get_translations(self):
        return Translations()

    def get_defalut_sales_counter_payment_method(self):
        for (pm_id, label) in self.sales_counter_payment_method_id.choices:
            pm = PaymentMethod.query.filter_by(id=pm_id).first()
            if pm and pm.payment_plugin_id == plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID:
                return pm_id
        return 0

    performance_id = HiddenField(
        validators=[Required()],
    )
    stocks = HiddenField(
        label='',
        validators=[Optional()],
    )
    note = TextAreaField(
        label=u'備考・メモ',
        validators=[
            Optional(),
            Length(max=2000, message=u'2000文字以内で入力してください'),
        ],
    )
    products = SelectMultipleField(
        label=u'商品',
        validators=[Optional()],
        choices=[],
        coerce=int
    )
    sales_segment_id = SelectField(
        label=u'販売区分',
        validators=[Required()],
        choices=[],
        coerce=lambda x : int(x) if x else u'',
    )
    payment_delivery_method_pair_id = SelectField(
        label=u'決済・引取方法',
        validators=[Required(u'決済・引取方法を選択してください')],
        choices=[],
        coerce=lambda x : int(x) if x else u'',
    )
    sales_counter_payment_method_id = SelectField(
        label=u'当日窓口決済',
        validators=[Optional()],
        choices=[],
        coerce=int,
    )
    last_name = TextField(
        label=u'姓',
        filters=[strip_spaces],
        validators=[
            Optional(),
            Zenkaku,
            Length(max=10, message=u'10文字以内で入力してください'),
        ],
    )
    last_name_kana = TextField(
        label=u'姓(カナ)',
        filters=[strip_spaces, NFKC],
        validators=[
            Optional(),
            Katakana,
            Length(max=10, message=u'10文字以内で入力してください'),
        ]
    )
    first_name = TextField(
        label=u'名',
        filters=[strip_spaces],
        validators=[
            Optional(),
            Zenkaku,
            Length(max=10, message=u'10文字以内で入力してください'),
        ]
    )
    first_name_kana = TextField(
        label=u'名(カナ)',
        filters=[strip_spaces, NFKC],
        validators=[
            Optional(),
            Katakana,
            Length(max=10, message=u'10文字以内で入力してください'),
        ]
    )
    tel_1 = TextField(
        label=u'TEL',
        filters=[ignore_space_hyphen],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'-(ハイフン)を抜いた半角数字のみを入力してください'),
        ]
    )

    def validate_stocks(form, field):
        if len(field.data) == 0:
            raise ValidationError(u'座席および席種を選択してください')
        #if len(field.data) > 1:
        #    raise ValidationError(u'複数の席種を選択することはできません')
        if not form.products.choices:
            raise ValidationError(u'選択された座席に紐づく予約可能な商品がありません')

    def validate_payment_delivery_method_pair_id(form, field):
        if field.data and field.data in field.sej_plugin_id:
            for field_name in ['last_name', 'first_name', 'last_name_kana', 'first_name_kana', 'tel_1']:
                f = getattr(form, field_name)
                if not f.data:
                    raise ValidationError(u'購入者情報を入力してください')

            # 決済せずにコンビニ受取できるのはadministratorのみ (不正行為対策)
            pdmp = PaymentDeliveryMethodPair.get(field.data)
            if pdmp\
                and pdmp.payment_method.payment_plugin_id != plugins.SEJ_PAYMENT_PLUGIN_ID\
                and pdmp.delivery_method.delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID\
                and not isinstance(has_permission('event_editor', form.request.context, form.request), ACLAllowed):
                    raise ValidationError(u'この決済引取方法を選択する権限がありません')

            # Sej発券の場合は20枚まで
            if pdmp.delivery_method.delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID:
                count = 0
                post_data = MultiDict(form.request.json_body)
                for product_id, product_name in form.products.choices:
                    product = Product.query.filter_by(id=product_id).one()
                    quantity = None
                    try:
                        quantity_str = post_data.get('product_quantity-%d' % product_id)
                        if quantity_str is not None:
                            quantity_str = quantity_str.strip()
                            if quantity_str:
                                quantity = int(quantity_str)
                    except (ValueError, TypeError):
                        raise ValidationError(u'個数には正しい数値を入力してください')
                    if not quantity:
                        continue
                    count += product.num_tickets(pdmp) * quantity
                if count > 20:
                    raise ValidationError(u'コンビニ引取の場合、1予約あたり発券枚数が20枚以内になるよう指定してください')


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
        label=u'配送手数料',
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
    start_at = DateField(
        label=u'払戻期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d',
        widget=OurDateWidget()
    )
    end_at = DateField(
        label=u'払戻期間',
        validators=[Optional(), after1900],
        format='%Y-%m-%d',
        missing_value_defaults=dict(
            year=u'',
            month=Max,
            day=Max
        ),
        widget=OurDateWidget()
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

            # コンビニ引取
            if settlement_delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID:
                if refund_order.is_issued():
                    # 発券済ならコンビニ払戻のみ可能
                    if refund_pm.payment_plugin_id != plugins.SEJ_PAYMENT_PLUGIN_ID:
                        raise ValidationError('%s: %s(%s)' % (error_msg, u'既にコンビニ発券済なのでコンビニ払戻を選択してください', refund_order.order_no))
            elif settlement_delivery_plugin_id == plugins.FAMIPORT_DELIVERY_PLUGIN_ID:
                if refund_order.is_issued():
                    # 発券済ならコンビニ払戻のみ可能
                    if refund_pm.payment_plugin_id != plugins.FAMIPORT_PAYMENT_PLUGIN_ID:
                        raise ValidationError('%s: %s(%s)' % (error_msg, u'既にコンビニ発券済なのでコンビニ払戻を選択してください', refund_order.order_no))
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
            if refund_pm.payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID:
                if not self.start_at.data:
                    self.start_at.errors.append(u'入力してください')
                    status = False
                if not self.end_at.data:
                    self.end_at.errors.append(u'入力してください')
                    status = False
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

    def _get_translations(self):
        return Translations()

    order_csv = FileField(
        u'CSVファイル',
        validators=[]
    )
    import_type = BugFreeSelectField(
        label=u'インポート方法',
        validators=[Required()],
        choices=[(str(e.v), get_import_type_label(e.v, no_option_desc=True)) for e in [ImportTypeEnum.Create, ImportTypeEnum.Update, ImportTypeEnum.CreateOrUpdate]],
        default=ImportTypeEnum.Create.v,
        coerce=int,
    )
    always_issue_order_no = OurBooleanField(
        label=u'常に新しい予約番号を発番'
    )
    allocation_mode = BugFreeSelectField(
        label=u'配席モード',
        validators=[Required()],
        choices=[(str(e.v), get_allocation_mode_label(e.v)) for e in AllocationModeEnum],
        default=ImportTypeEnum.Create.v,
        coerce=int,
    )
    merge_order_attributes = OurBooleanField(
        label=u'既存の予約の購入情報属性を更新する',
        help=u'チェックを入れずに実行すると、属性はCSVに書かれているものに置換となりますので注意してください',
        default=True
    )

    def validate_order_csv(form, field):
        if not hasattr(field.data, 'file'):
            raise ValidationError(u'選択してください')

        if len(field.data.file.readlines()) < 2:
            raise ValidationError(u'データがありません')
        field.data.file.seek(0)

        # ヘッダーをチェック
        reader = ImportCSVReader(field.data.file)
        import_header = reader.fieldnames
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

        difference = set(import_header) - set(export_header)
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

    #tickets = FieldList(FormField(SejTicketForm), min_entries=20)



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
