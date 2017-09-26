# -*- coding:utf-8 -*-

""" PC/Mobile のスーパービュークラス
"""
import logging
import functools
from datetime import date, datetime, time
from pyramid.interfaces import IRouteRequest, IRoutesMapper
from pyramid.httpexceptions import HTTPFound
from pyramid.decorator import reify
from pyramid.threadlocal import get_current_request, get_current_registry
from pyramid.i18n import TranslationString as _
from zope.interface import providedBy, directlyProvides
from sqlalchemy.sql.expression import desc, asc
from sqlalchemy.orm import joinedload, aliased
from wtforms import widgets as wt_widgets
from wtforms.fields import core as wt_fields
from altair.app.ticketing.core import models as c_models
from altair.sqlahelper import get_db_session
from altair.mobile.interfaces import IMobileRequest
from altair.viewhelpers.datetime_ import create_date_time_formatter
from altair.formhelpers.form import OurDynamicForm
from altair.formhelpers import widgets
from altair.formhelpers import fields
from altair.formhelpers.filters import text_type_but_none_if_not_given
from altair.formhelpers.validators import Required, DynSwitchDisabled, HIRAGANAS_REGEXP, KATAKANAS_REGEXP, ALPHABETS_REGEXP, NUMERICS_REGEXP
from altair.formhelpers.widgets.datetime import (
    DateFieldBuilder,
    DateSelectFormElementBuilder,
    )
from wtforms.validators import Optional, Regexp, Length
from altair.formhelpers.translations import Translations
from markupsafe import Markup
from altair.app.ticketing.models import DBSession
from . import helpers as h
from . import api
from collections import OrderedDict
from .exceptions import (
    NoEventError,
    QuantityOutOfBoundsError,
    ProductQuantityOutOfBoundsError,
    PerStockTypeQuantityOutOfBoundsError,
    PerStockTypeProductQuantityOutOfBoundsError,
    PerProductProductQuantityOutOfBoundsError,
    )
from .resources import PerformanceOrientedTicketingCartResource
from .interfaces import ICartResource

logger = logging.getLogger(__name__)

build_date_input_select = DateFieldBuilder(DateSelectFormElementBuilder(placeholders=True))

class IndexViewMixin(object):
    def __init__(self):
        self._event_extra_info = None

    def prepare(self):
        self._clear_temporary_store()
        self._check_redirect()

    def _fetch_event_info(self):
        if self._event_extra_info is None:
            if self.context.event is None:
                event_extra_info = {}
            else:
                from .api import get_event_info_from_cms
                event_extra_info = get_event_info_from_cms(self.request, self.context.event.id)
                if not event_extra_info:
                    event_extra_info = {}
            self._event_extra_info = event_extra_info
            logger.info(self._event_extra_info)

    def _clear_temporary_store(self):
        from .api import get_temporary_store
        get_temporary_store(self.request).clear(self.request)

    def _check_redirect(self):
        mobile = IMobileRequest.providedBy(self.request)
        if isinstance(self.request.context, PerformanceOrientedTicketingCartResource):
            performance_id = self.request.context.performance and self.request.context.performance.id
        else:
            performance_id = self.request.params.get('pid') or self.request.params.get('performance')

        if performance_id:
            specified = c_models.Performance.query.filter(c_models.Performance.id==performance_id).filter(c_models.Performance.public==True).first()
            if mobile:
                if specified is not None and specified.redirect_url_mobile:
                    raise HTTPFound(specified.redirect_url_mobile)
            else:
                if specified is not None and specified.redirect_url_pc:
                    raise HTTPFound(specified.redirect_url_pc)

    @reify
    def event_extra_info(self):
        self._fetch_event_info()
        return self._event_extra_info


def get_amount_without_pdmp(cart):
    return sum([cp.product.price * cp.quantity for cp in cart.items])

def get_seat_type_dicts(request, sales_segment, seat_type_id=None):
    # TODO: cachable
    slave_session = get_db_session(request, 'slave')
    q = slave_session.query(c_models.StockType, c_models.Product, c_models.ProductItem, c_models.Stock, c_models.StockStatus.quantity) \
        .filter(c_models.StockType.display == True) \
        .filter(c_models.Product.public == True) \
        .filter(c_models.Product.deleted_at == None) \
        .filter(c_models.ProductItem.product_id==c_models.Product.id) \
        .filter(c_models.ProductItem.stock_id==c_models.Stock.id) \
        .filter(c_models.ProductItem.deleted_at == None) \
        .filter(c_models.Stock.stock_type_id==c_models.StockType.id) \
        .filter(c_models.Stock.deleted_at == None) \
        .filter(c_models.StockHolder.id==c_models.Stock.stock_holder_id) \
        .filter(c_models.StockHolder.deleted_at == None) \
        .filter(c_models.StockStatus.stock_id==c_models.Stock.id) \
        .filter(c_models.Product.sales_segment_id == sales_segment.id) \
        .order_by(
            asc(c_models.StockType.display_order),
            asc(c_models.Product.display_order),
            desc(c_models.Product.price)
            )

    if ICartResource.providedBy(request.context):
        context = request.context
    else:
        context = None

    if seat_type_id is not None:
        _ProductItem = aliased(c_models.ProductItem)
        _Product = aliased(c_models.Product)
        _Stock = aliased(c_models.Stock)
        q = q.filter(c_models.Product.id.in_(
            slave_session.query(_Product.id) \
            .filter(_Product.id == _ProductItem.product_id) \
            .filter(_ProductItem.stock_id == _Stock.id) \
            .filter(_Stock.stock_type_id == seat_type_id) \
            .distinct()))

    stock_types = OrderedDict()
    products_for_stock_type = dict()
    product_items_for_product = dict()
    stock_for_product_item = dict()
    stocks_for_stock_type = dict()
    availability_for_stock = dict()

    availability_per_product_map = dict()
    for stock_type, product, product_item, stock, available in q:
        if stock_type.id not in stock_types:
            stock_types[stock_type.id] = stock_type

        products = products_for_stock_type.get(stock_type.id)
        if products is None:
            products = products_for_stock_type[stock_type.id] = OrderedDict()
        products[product.id] = product

        product_items = product_items_for_product.get(product.id)
        if product_items is None:
            product_items = product_items_for_product[product.id] = []
        product_items.append(product_item)

        stock_for_product_item[product_item.id] = stock

        availability_per_product = availability_per_product_map.get(product.id)
        if availability_per_product is None:
            availability_per_product = available / product_item.quantity
        else:
            availability_per_product = min(availability_per_product, available)
        availability_per_product_map[product.id] = availability_per_product

        if stock.id not in availability_for_stock:
            availability_for_stock[stock.id] = available

        stocks = stocks_for_stock_type.get(stock_type.id)
        if stocks is None:
            stocks = stocks_for_stock_type[stock_type.id] = []
        stocks.append(stock.id)

    max_quantity_per_user = None
    # このクエリが重い可能性が高いので、一時的に蓋閉め
    # if context is not None:
    #     # container can be a SalesSegment, Performance or Event...
    #     l = [
    #         record['max_quantity_per_user'] - record['total_quantity']
    #         for container, record in context.get_total_orders_and_quantities_per_user(sales_segment)
    #         if record['max_quantity_per_user'] is not None
    #         ]
    #     if l:
    #         max_quantity_per_user = min(l)

    retval = []
    for stock_type in stock_types.itervalues():
        availability_for_stock_type = 0
        actual_availability_for_stock_type = 0
        actual_stocks_for_stock_type = set()
        product_dicts = []
        min_product_quantity = stock_type.min_product_quantity
        max_product_quantity = stock_type.max_product_quantity
        min_quantity = stock_type.min_quantity
        max_quantity = stock_type.max_quantity

        # ユーザ毎の最大購入枚数があれば、それを加味する...
        if max_quantity_per_user is not None:
            max_quantity = max(max_quantity, max_quantity_per_user)
        for product in products_for_stock_type[stock_type.id].itervalues():
            # XXX: 券種導入時に直す
            quantity_power = sum(
                product_item.quantity
                for product_item in product_items_for_product[product.id]
                if stock_for_product_item[product_item.id].stock_type_id == \
                        product.seat_stock_type_id \
                   or product.seat_stock_type_id is None
                )
            if quantity_power == 0:
                logger.warning("quantity power=0! sales_segment.id=%ld, product.id=%ld", sales_segment.id, product.id)
                quantity_power = 1
            stocks = set(
                stock_for_product_item[product_item.id]
                for product_item in product_items_for_product[product.id]
                if stock_for_product_item[product_item.id].stock_type_id == \
                        product.seat_stock_type_id \
                   or product.seat_stock_type_id is None
                )
            availability = availability_per_product_map[product.id]
            max_product_quatity = sales_segment.max_product_quatity

            # 現在のところ、商品毎に下限枚数や上限枚数は指定できないので
            min_quantity_per_product = min_quantity or 0
            max_quantity_per_product = availability * quantity_power
            if max_quantity is not None:
                max_quantity_per_product = min(max_quantity_per_product, max_quantity)

            # 購入上限枚数は販売区分ごとに設定できる
            if sales_segment.max_quantity is not None:
                max_quantity_per_product = min(max_quantity_per_product, sales_segment.max_quantity)

            # 商品毎の商品購入下限数を計算する
            min_product_quantity_per_product = (min_quantity_per_product + quantity_power - 1) / quantity_power
            if min_product_quantity is not None:
                min_product_quantity_per_product = max(min_product_quantity_per_product, min_product_quantity)
            if product.min_product_quantity is not None:
                min_product_quantity_per_product = max(min_product_quantity_per_product, product.min_product_quantity)
            if product.must_be_chosen:
                min_product_quantity_per_product = max(1, min_product_quantity_per_product)

            # 商品毎の商品購入上限数を計算する
            max_product_quantity_per_product = max_quantity_per_product / quantity_power
            if max_product_quatity is not None:
                max_product_quantity_per_product = min(max_product_quantity_per_product, max_product_quatity)
            if max_product_quantity is not None:
                max_product_quantity_per_product = min(max_product_quantity_per_product, max_product_quantity)
            if product.max_product_quantity is not None:
                max_product_quantity_per_product = min(max_product_quantity_per_product, product.max_product_quantity)

            # 席種毎の残数は商品在庫の最大値
            availability_for_stock_type = max(availability_for_stock_type, availability)

            # 下限や上限を加味した在庫数
            actual_availability = availability
            # 購入下限が購入上限を超えてしまっていたり下限数を割っている席種は購入不可にしたい
            if max_product_quantity_per_product < min_product_quantity_per_product or \
               max_quantity_per_product < min_quantity_per_product or \
               actual_availability * quantity_power < min_quantity_per_product or \
               actual_availability < min_product_quantity_per_product:
                actual_availability = 0
                stocks = set()
            actual_availability_for_stock_type = max(actual_availability_for_stock_type, actual_availability)
            for stock in stocks:
                actual_stocks_for_stock_type.add(stock)


            per_stock_element_descs = {}

            for product_item in product_items_for_product[product.id]:
                per_stock_element_desc = per_stock_element_descs.get(product_item.stock_id)
                if per_stock_element_desc is None:
                    stock = stock_for_product_item[product_item.id]
                    stock_type_id = stock.stock_type_id
                    per_stock_element_desc = per_stock_element_descs[product_item.stock_id] = \
                        dict(
                            quantity=product_item.quantity,
                            is_primary_seat_stock_type=(stock_type_id == product.seat_stock_type_id),
                            is_seat_stock_type=(not stock_types[stock_type_id].quantity_only)
                            )
                else:
                    per_stock_element_desc['quantity'] += product_item.quantity

            product_dicts.append(
                dict(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    must_be_chosen=product.must_be_chosen,
                    price=h.format_number(product.price, ","),
                    detail=None,
                    unit_template=h.build_unit_template(product_items_for_product[product.id]),
                    quantity_power=quantity_power,
                    max_quantity=max_product_quantity_per_product,
                    max_product_quatity=max_product_quatity,
                    min_product_quantity_from_product= product.min_product_quantity if not product.must_be_chosen else max(1, product.min_product_quantity),
                    max_product_quantity_from_product=product.max_product_quantity,
                    min_product_quantity_per_product=min_product_quantity_per_product,
                    max_product_quantity_per_product=max_product_quantity_per_product,
                    elements=per_stock_element_descs,
                    product_items_count=len(product.items),
                    first_product_item_sell_unit=product.items[0].quantity if len(product.items) >= 1 else None
                    )
                )

        event_setting = sales_segment.performance.event.setting
        total_availability_for_stock_type = sum([availability_for_stock.get(actual_stock.id) for actual_stock in actual_stocks_for_stock_type])
        total_quantity_for_stock_type = sum([actual_stock.quantity for actual_stock in actual_stocks_for_stock_type])
        middle_stock_threshold = event_setting.middle_stock_threshold if event_setting else None
        middle_stock_threshold_percent = event_setting.middle_stock_threshold_percent if event_setting else None
        retval.append(dict(
            id=stock_type.id,
            name=stock_type.name,
            description=stock_type.description,
            style=stock_type.style,
            stocks=stocks_for_stock_type[stock_type.id],
            availability=availability_for_stock_type,
            actual_availability=actual_availability_for_stock_type,
            availability_text=h.get_availability_text(total_availability_for_stock_type, total_quantity_for_stock_type, middle_stock_threshold, middle_stock_threshold_percent),
            quantity_only=stock_type.quantity_only,
            seat_choice=sales_segment.seat_choice,
            products=product_dicts,
            min_quantity=min_quantity,
            max_quantity=max_quantity,
            min_product_quantity=min_product_quantity,
            max_product_quantity=max_product_quantity
            ))

    if seat_type_id is not None:
        retval = [stock_type_dict for stock_type_dict in retval if stock_type_dict['id'] == seat_type_id]

    return retval


def assert_quantity_within_bounds(sales_segment, order_items):
    # 購入枚数の制限
    sum_quantity = 0
    sum_product_quantity = 0
    quantities_per_stock_type = {}
    stock_types = {}
    for product, quantity in order_items:
        stock_type = product.seat_stock_type # XXX: 券種導入時になんとかする
        quantity_power = product.get_quantity_power(stock_type, product.performance_id)
        sum_quantity += quantity * quantity_power
        sum_product_quantity += quantity
        if stock_type is not None:
            # 券種が特定できる商品のみ検証する
            quantity_per_stock_type = quantities_per_stock_type.get(stock_type.id)
            if quantity_per_stock_type is None:
                quantities_per_stock_type[stock_type.id] = quantity_per_stock_type = {
                    'quantity': 0,
                    'product_quantity': 0
                    }
            stock_types[stock_type.id] = stock_type
            quantity_per_stock_type['quantity'] += quantity * quantity_power
            quantity_per_stock_type['product_quantity'] += quantity
        if (product.min_product_quantity is not None and product.must_be_chosen and quantity < product.min_product_quantity) or \
            (not product.must_be_chosen and quantity != 0 and quantity < product.min_product_quantity):
            raise PerProductProductQuantityOutOfBoundsError(
                quantity,
                product.min_product_quantity,
                product.max_product_quantity
                )
        if (product.min_product_quantity is None and product.must_be_chosen and quantity == 0):
            raise PerProductProductQuantityOutOfBoundsError(
                quantity,
                1,
                product.max_product_quantity
            )
        if product.max_product_quantity is not None and \
           quantity > product.max_product_quantity:
            raise PerProductProductQuantityOutOfBoundsError(
                quantity,
                product.min_product_quantity,
                product.max_product_quantity
                )

    logger.debug('sum_quantity=%d, sum_product_quantity=%d' % (sum_quantity, sum_product_quantity))

    if sum_quantity == 0:
        raise QuantityOutOfBoundsError(sum_quantity, 1, sales_segment.max_quantity)

    if sales_segment.max_quantity is not None and \
       sales_segment.max_quantity < sum_quantity:
        raise QuantityOutOfBoundsError(sum_quantity, 1, sales_segment.max_quantity)

    if sales_segment.max_product_quatity is not None and \
       sales_segment.max_product_quatity < sum_product_quantity:
        raise ProductQuantityOutOfBoundsError(sum_product_quantity, 1, sales_segment.max_product_quatity)

    for stock_type_id, quantity_per_stock_type in quantities_per_stock_type.items():
        stock_type = stock_types[stock_type_id]
        if stock_type.min_quantity is not None and \
           stock_type.min_quantity > quantity_per_stock_type['quantity']:
            raise PerStockTypeQuantityOutOfBoundsError(
                quantity_per_stock_type['quantity'],
                stock_type.min_quantity,
                stock_type.max_quantity
                )
        if stock_type.max_quantity is not None and \
           stock_type.max_quantity < quantity_per_stock_type['quantity']:
            raise PerStockTypeQuantityOutOfBoundsError(
                quantity_per_stock_type['quantity'],
                stock_type.min_quantity,
                stock_type.max_quantity
                )
        if stock_type.min_product_quantity is not None and \
           stock_type.min_product_quantity > quantity_per_stock_type['product_quantity']:
            raise PerStockTypeProductQuantityOutOfBoundsError(
                quantity_per_stock_type['product_quantity'],
                stock_type.min_product_quantity,
                stock_type.max_product_quantity
                )
        if stock_type.max_product_quantity is not None and \
           stock_type.max_product_quantity < quantity_per_stock_type['product_quantity']:
            raise PerStockTypeProductQuantityOutOfBoundsError(
                quantity_per_stock_type['product_quantity'],
                stock_type.min_product_quantity,
                stock_type.max_product_quantity
                )


class DynamicFormBuilder(object):
    _base_form_factory = OurDynamicForm
    validator_specs = [
        ('numerics', NUMERICS_REGEXP, u'数字'),
        ('alphabets', ALPHABETS_REGEXP, u'英文字'),
        ('hiragana', HIRAGANAS_REGEXP, u'ひらがな'),
        ('katakana', KATAKANAS_REGEXP, u'カタカナ'),
        ('other_characters', None, None),
        ]

    @staticmethod
    def _name_builder(name):
        return u'extra_field[%s]' % name

    def _form_factory(self, **kwargs):
        return self._base_form_factory(name_builder=self._name_builder, **kwargs)

    def __init__(self, form_factory=None):
        if form_factory is None:
            form_factory = self._form_factory
        self.form_factory = form_factory

    def _convert_choices(self, choice_descs):
        return [(choice_desc['value'], choice_desc['label']) for choice_desc in choice_descs]

    def _build_validators(self, field_desc):
        validators = []
        activation_conditions = field_desc.get('activation_conditions')
        if activation_conditions:
            validators.append(DynSwitchDisabled(u'NOT(%s)' % activation_conditions))
        if field_desc['required']:
            validators.append(Required())

        if field_desc.get('kind') in ['text', 'textarea', 'password']:
            max = field_desc.get('max_length')
            message = u'{}文字以内で入力してください'.format(max)
            validators.append(Length(max=max, message=message))

        validator_flags = {}
        all_enabled = True
        validator_descs = field_desc.get('validators')
        if validator_descs:
            for name, _, _ in self.validator_specs:
                enabled = validator_descs.get(name, {}).get('enabled', True)
                validator_flags[name] = enabled
                all_enabled = all_enabled and enabled
        if not all_enabled:
            concatenated_csets = ur''
            message = u''
            if validator_flags['other_characters']:
                sets = [u'[^']
                cdescs = []
                for name, cset, cdesc in self.validator_specs:
                    if cset is not None and not validator_flags[name]:
                        sets.append(cset)
                        cdescs.append(cdesc)
                sets.append(u']')
                concatenated_csets = u''.join(sets)
                message = u'%sは入力できません' % u'・'.join(cdescs)
            else:
                sets = [u'^[']
                cdescs = []
                for name, cset, cdesc in self.validator_specs:
                    if cset is not None and validator_flags[name]:
                        sets.append(cset)
                        cdescs.append(cdesc)
                sets.append(u']+$')
                concatenated_csets = u''.join(sets)
                message = u'%sのみ入力できます' % u'・'.join(cdescs)
            validators.append(Regexp(concatenated_csets, message=message))

        if not field_desc['required']:
            validators.append(Optional())

        return validators

    def _build_text(self, field_desc):
        return fields.OurTextField(
            label=field_desc['display_name'],
            description=field_desc['description'] and Markup(field_desc['description']),
            note=field_desc['note'] and Markup(field_desc['note']),
            validators=self._build_validators(field_desc)
            )

    def _build_password(self, field_desc):
        return fields.OurTextField(
            label=field_desc['display_name'],
            description=field_desc['description'] and Markup(field_desc['description']),
            note=field_desc['note'] and Markup(field_desc['note']),
            validators=self._build_validators(field_desc),
            widget=widgets.OurPasswordInput()
            )

    def _build_textarea(self, field_desc):
        return fields.OurTextAreaField(
            label=field_desc['display_name'],
            description=field_desc['description'] and Markup(field_desc['description']),
            note=field_desc['note'] and Markup(field_desc['note']),
            validators=self._build_validators(field_desc)
            )

    def _build_select(self, field_desc):
        return fields.OurSelectField(
            label=field_desc['display_name'],
            description=field_desc['description'] and Markup(field_desc['description']),
            note=field_desc['note'] and Markup(field_desc['note']),
            validators=self._build_validators(field_desc),
            choices=self._convert_choices(field_desc['choices'])
            )

    def _build_multiple_select(self, field_desc):
        return fields.OurSelectMultipleField(
            label=field_desc['display_name'],
            description=field_desc['description'] and Markup(field_desc['description']),
            note=field_desc['note'] and Markup(field_desc['note']),
            validators=self._build_validators(field_desc),
            choices=self._convert_choices(field_desc['choices'])
            )

    def _build_radio(self, field_desc):
        return fields.OurRadioField(
            label=field_desc['display_name'],
            description=field_desc['description'] and Markup(field_desc['description']),
            note=field_desc['note'] and Markup(field_desc['note']),
            validators=self._build_validators(field_desc),
            choices=self._convert_choices(field_desc['choices']),
            coerce=text_type_but_none_if_not_given
            )

    def _build_checkbox(self, field_desc):
        return fields.OurSelectMultipleField(
            label=field_desc['display_name'],
            description=field_desc['description'] and Markup(field_desc['description']),
            note=field_desc['note'] and Markup(field_desc['note']),
            validators=self._build_validators(field_desc),
            choices=self._convert_choices(field_desc['choices']),
            widget=widgets.CheckboxMultipleSelect(
                multiple=True,
                outer_html_tag='ul',
                inner_html_tag='li'
                )
            )

    def _build_date(self, field_desc):
        return fields.OurDateField(
            label=field_desc['display_name'],
            description=field_desc['description'] and Markup(field_desc['description']),
            note=field_desc['note'] and Markup(field_desc['note']),
            validators=self._build_validators(field_desc),
            default=None,
            missing_value_defaults=dict(year=None, month=None, day=None),
            widget=widgets.OurDateWidget(
                input_builder=build_date_input_select
                )
            )

    field_factories = {
        u'text': _build_text,
        u'password': _build_password,
        u'textarea': _build_textarea,
        u'select': _build_select,
        u'multiple_select': _build_multiple_select,
        u'radio': _build_radio,
        u'checkbox': _build_checkbox,
        u'date': _build_date,
        }

    def unbound_fields(self, extra_form_fields):
        unbound_fields = []
        for field_desc in extra_form_fields:
            if field_desc['kind'] != 'description_only':
                unbound_fields.append(
                    (
                        field_desc['name'],
                        self.field_factories.get(
                            field_desc['kind'],
                            self.__class__._build_text
                            )(self, field_desc)
                        )
                    )
        return unbound_fields

    def __call__(self, request, extra_form_fields, formdata=None, **kwargs):
        """
        :param request: リクエストオブジェクト
        :param list extra_form_fields: ExtraFormのリスト
        """
        unbound_fields = self.unbound_fields(extra_form_fields)
        form = self.form_factory(
            formdata=formdata,
            _fields=unbound_fields,
            _translations=Translations(),
            **kwargs
            )
        fields = []
        for field_desc in extra_form_fields:
            field = None
            try:
                field = form[field_desc['name']]
            except KeyError:
                pass
            fields.append({
                'required': field_desc['required'],
                'description': Markup(field_desc['description']) if field is None else None,
                'field': field,
                'descriptor': field_desc,
                })
        return form, fields

build_dynamic_form = DynamicFormBuilder()

class DummyForm(object):
    def __init__(self, context):
        self.context = context

    def _get_translations(self):
        return None


class DummyCartContext(object):
    def __init__(self, request, order):
        self.request = request
        self.order = order

    @property
    def available_payment_delivery_method_pairs(self):
        return self.order.sales_segment.payment_delivery_method_pairs

    @property
    def available_sales_segments(self):
        return [self.order.sales_segment]

    @property
    def cart_setting(self):
        return self.order.cart_setting


def build_extra_form_fields_from_form(context, request, form_class, excludes=()):
    retval = []
    form = None
    _fields = sorted(
        (
            (k, getattr(form_class, k))
            for k in dir(form_class)
            if isinstance(getattr(form_class, k), wt_fields.UnboundField) and k not in excludes
            ),
        key=lambda pair: pair[1].creation_counter
        )
    for k, field in _fields:
        if len(field.args) >= 1:
            label = field.args[0]
        elif 'label' in field.kwargs:
            label = field.kwargs['label']
        else:
            label = k
        if len(field.args) >= 7:
            widget = field.args[6]
        elif 'widget' in field.kwargs:
            widget = field.kwargs['widget']
        else:
            widget = field.field_class.widget
        if isinstance(widget, widgets.Switcher):
            widget = sorted(widget.widgets.values(), key=lambda v: 1 if isinstance(v, wt_widgets.TextInput) else 0)[0]
        description = field.kwargs.get('description', None)
        note = field.kwargs.get('note', None)
        kind = None
        choices = None
        if issubclass(field.field_class, (fields.OurTextField, wt_fields.StringField)):
            if isinstance(widget, (widgets.OurTextArea, wt_widgets.TextArea)):
                kind = 'textarea'
            elif isinstance(widget, (widgets.OurTextInput, wt_widgets.TextInput)):
                kind = 'text'
            elif isinstance(widget, (widgets.OurPasswordInput, wt_widgets.PasswordInput)):
                kind = 'password'
        elif issubclass(field.field_class, (fields.OurIntegerField, wt_fields.IntegerField)):
            if isinstance(widget, (wt_widgets.TextInput, widgets.OurTextInput)):
                kind = 'text'
        elif issubclass(field.field_class, wt_fields.RadioField):
            kind = 'radio'
            choices = field.kwargs.get('choices')
        elif issubclass(field.field_class, wt_fields.SelectFieldBase):
            kind = 'select'
            choices = field.kwargs.get('choices')
        elif issubclass(field.field_class, wt_fields.SelectMultipleField):
            if isinstance(widget, wt_widgets.Select):
                kind = 'multiple_select'
            elif isinstance(widget, widgets.CheckboxMultipleSelect):
                kind = 'checkbox'
            choices = field.kwargs.get('choices')
        elif issubclass(field.field_class, fields.OurDateField):
            kind = 'date'
        elif issubclass(field.field_class, fields.OurDateTimeField):
            kind = 'datetime'
        elif issubclass(field.field_class, fields.OurTimeField):
            kind = 'time'
        elif issubclass(field.field_class, wt_fields.BooleanField):
            kind = 'bool'
        if kind is None:
            raise TypeError('unsupported field / widget combination: %s - %s' % (field.field_class, widget))
        if choices is not None and callable(choices):
            # 選択肢が動的に生成されるケース
            # form_class の実装がわからないのでいろいろなパターンを試してインスタンス化する...
            if form is None:
                dummy_form = DummyForm(context)
                try:
                    dummy_form_field = fields.OurFormField(lambda **kwargs: form_class(context=context, **kwargs)).bind(dummy_form, '')
                    dummy_form_field.process(None)
                    form = dummy_form_field._contained_form
                    assert form is not None
                except TypeError:
                    try:
                        dummy_form_field = fields.OurFormField(form_class).bind(dummy_form, '')
                        dummy_form_field.process(None)
                        form = dummy_form_field._contained_form
                        assert form is not None
                    except TypeError:
                        pass
                if form is None:
                    try:
                        form = form_class(context=context)
                    except TypeError:
                        form = form_class()
            choices = getattr(form, k).choices
        retval.append({
            'name': k,
            'kind': kind,
            'display_name': label,
            'choices': [{'value': value, 'label': label} for value, label in choices] if choices is not None else None,
            'description': description,
            'note': note,
            })
    return retval

def get_extra_form_class(request, cart_setting):
    from .schemas import extra_form_type_map
    return extra_form_type_map.get(cart_setting.type)

def filter_extra_form_schema(extra_form_fields, mode=None):
    if mode is None:
        # XXX: デフォルトを entry に変えるべきでは?
        mode = 'any'

    if isinstance(mode, basestring):
        modes = mode.split(',')
    else:
        modes = mode

    bitmask = 0
    for mode in modes:
        if mode == 'entry':
            bitmask |= 1 
        elif mode == 'orderreview':
            bitmask |= 2
        elif mode == 'editable':
            bitmask |= 4
        elif mode == 'any':
            bitmask |= 7
        else:
            raise ValueError('invalid mode: %s' % mode)

    return [
        field_desc
        for field_desc in extra_form_fields
        if ((1 if field_desc.get('show_on_entry', True) else 0) \
             | (2 if field_desc.get('show_in_orderreview', True) else 0) \
             | (4 if field_desc.get('edit_in_orderreview', False) else 0)) & bitmask != 0
        ]

def get_extra_form_schema(context, request, sales_segment, for_=None):
    if for_ is None:
        for_ = 'cart'
    extra_form_fields = None
    cart_setting = context.cart_setting
    if for_ == 'cart':
        if api.is_fc_cart(cart_setting):
            return cart_setting.extra_form_fields
        elif api.is_booster_cart(cart_setting):
            # XXX: ブースターの互換性のため
            extra_form_class = get_extra_form_class(request, cart_setting)
            if extra_form_class is not None:
                extra_form_fields = build_extra_form_fields_from_form(context, request, extra_form_class, excludes=['member_type', 'product_delivery_method'])
        else:
            extra_form_fields = sales_segment.setting.extra_form_fields
    elif for_ == 'lots':
        extra_form_fields = cart_setting.extra_form_fields
    else:
        raise ValueError("for_ argument must be either 'cart' or 'lots', got %s" % for_)
    return extra_form_fields or []

def render_display_value(request, field_desc, field_value):
    display_value = None
    dtf = request.environ.get('render_display_value.dtf')
    if dtf is None:
        request.environ['render_display_value.dtf'] = dtf = create_date_time_formatter(request)
    if field_desc['kind'] in ('text', 'textarea'):
        display_value = field_value
    elif field_desc['kind'] == 'password':
        display_value = u'*' * len(field_value) if field_value else u''
    elif field_desc['kind'] in ('select', 'radio'):
        v = [pair for pair in field_desc['choices'] if pair['value'] == field_value]
        if len(v) > 0:
            display_value = v[0]['label']
        else:
            display_value = field_value
    elif field_desc['kind'] in ('multiple_select', 'checkbox'):
        display_value = []
        i = None
        try:
            # 後からフィールドが追加されたりする場合もあるのでチェックする
            i = iter(field_value)
        except TypeError:
            pass

        if i is not None:
            for c in i:
                v = [pair for pair in field_desc['choices'] if pair['value'] == c]
                if len(v) > 0:
                    v = v[0]['label']
                else:
                    v = c
                display_value.append(v)
    elif field_desc['kind'] == 'date':
        display_value = dtf.format_date(field_value) if field_value is not None else _(u'未入力')
    elif field_desc['kind'] == 'datetime':
        display_value = dtf.format_datetime(field_value) if field_value is not None else _(u'未入力')
    elif field_desc['kind'] == 'time':
        display_value = dtf.format_time(field_value) if field_value is not None else _(u'未入力')
    elif field_desc['kind'] == 'bool':
        # only for booster compatibility
        display_value = u'はい' if field_value else u'いいえ'
    else:
        logger.warning('unsupported kind: %s' % field_desc['kind'])
        display_value = field_value
    return display_value 

def get_extra_form_data_pair_pairs(context, request, sales_segment, data, for_='cart', mode=None):
    extra_form_fields = get_extra_form_schema(context, request, sales_segment, for_=for_)
    extra_form_fields = filter_extra_form_schema(extra_form_fields, mode)
    retval = []
    for field_desc in extra_form_fields:
        if field_desc['kind'] == 'description_only':
            continue
        field_value = data.get(field_desc['name'])
        display_value = render_display_value(request, field_desc, field_value)
        retval.append(
            (
                (
                    field_desc['name'],
                    field_value
                ),
                (
                    field_desc['display_name'],
                    display_value
                )
                )
            )
    return retval

def back_to_top(request):
    event_id = None
    performance_id = None

    try:
        event_id = long(request.matchdict.get('event_id'))
    except (ValueError, TypeError):
        pass
    if isinstance(request.context, PerformanceOrientedTicketingCartResource) and \
       request.context.performance:
        performance_id = request.context.performance.id
    else:
        try:
            performance_id = long(request.params.get('pid') or request.params.get('performance'))
        except (ValueError, TypeError):
            pass

    if event_id is None:
        if performance_id is None:
            cart = api.get_cart(request)
            if cart is not None:
                performance_id = cart.performance.id
                event_id = cart.performance.event_id
        else:
            try:
                event_id = DBSession.query(c_models.Performance).filter_by(id=performance_id).one().event_id
            except:
                pass

    extra = {}
    if performance_id is not None:
        extra['_query'] = { 'performance': performance_id }

    api.remove_cart(request)

    if api.is_spa_mode(request):
        return HTTPFound(performance_id and request.route_url('cart.spa.index', performance_id=performance_id, anything='') or request.context.host_base_url or "/", headers=request.response.headers)
    else:
        return HTTPFound(event_id and request.route_url('cart.index', event_id=event_id, **extra) or request.context.host_base_url or "/", headers=request.response.headers)

def back(pc=back_to_top, mobile=None):
    if mobile is None:
        mobile = pc

    def factory(func):
        @functools.wraps(func)
        def retval(*args, **kwargs):
            request = get_current_request()
            if request.params.has_key('back'):
                if IMobileRequest.providedBy(request):
                    return mobile(request)
                else:
                    return pc(request)
            return func(*args, **kwargs)
        return retval
    return factory

def gzip_preferred(request, response):
    if 'gzip' in request.accept_encoding:
        response.encode_content('gzip')

import cookielib
from pyramid.view import render_view_to_response
from webob.cookies import Cookie

default_cookie_policy = cookielib.DefaultCookiePolicy(netscape=True, rfc2965=True)

class RequestWrapper(object):
    """Wraps a WebOb request so it impersonates an urllib2's Request object"""
    def __init__(self, request):
        self.request = request

    def get_full_url(self):
        return self.request.url

    def get_host(self):
        return self.request.host

    def is_unverifiable(self):
        return False

class MorselWrapper(object):
    def __init__(self, morsel, request):
        self.morsel = morsel
        self.request = request
        _domain, colon, port = request.host.partition(':')
        if self.morsel.domain:
            domain = self.morsel.domain
            domain_specified = True
            domain_initial_dot = domain.startswith('.')
            if not domain_initial_dot:
                domain = '.' + domain
        else:
            domain = _domain
            domain_specified = False
            domain_initial_dot = False
        self.domain = domain
        self.domain_specified = domain_specified
        self.domain_initial_dot = domain_initial_dot
        self.port = port or None
        self.port_specified = bool(port)

    @property
    def name(self):
        return self.morsel.name

    @property
    def value(self):
        return self.morsel.value

    @property
    def comment(self):
        return self.morsel.comment

    @property
    def secure(self):
        return self.morsel.secure

    @property
    def path(self):
        return self.morsel.path

    @property
    def path_specified(self):
        return self.morsel.path is not None

    @property
    def version(self):
        return 1 # always supposed to be a cookie

    def get_nonstandard_attr(self, name, default=None):
        name = name.lower()
        if name == 'httponly':
            return self.morsel.httponly
        elif name == 'max-age':
            return self.morsel.max_age
        return default


def render_view_to_response_with_derived_request(context_factory, request, name='', secured=False, route=None, retoucher=None, cookie_policy=default_cookie_policy):
    if hasattr(request, 'registry'):
        registry = request.registry
    else:
        registry = get_current_registry()
    subrequest = request.copy()
    response = request.response
    subrequest.response = request.response
    subrequest.registry = registry
    for k in set(dir(request)).difference(dir(subrequest)):
        setattr(subrequest, k, getattr(request, k))
    provides = list(providedBy(request))
    if route is not None:
        request_iface = registry.getUtility(IRouteRequest, route[0])
        provides.append(request_iface)
        mapper = registry.getUtility(IRoutesMapper)
        route_ = mapper.get_route(route[0])
        subrequest.environ['PATH_INFO'] = route_.generate(route[1])
    directlyProvides(subrequest, provides)
    if retoucher is not None:
        retoucher(subrequest)
    cookies_going_to_be_sent = response.headers.getall('Set-Cookie')
    u2req = RequestWrapper(subrequest)
    cookies_to_set = {}
    if cookies_going_to_be_sent:
        for set_cookie_header_value in cookies_going_to_be_sent:
            cookies = Cookie()
            cookies.load(set_cookie_header_value)
            for m in cookies.values():
                if cookie_policy.set_ok(MorselWrapper(m, subrequest), u2req):
                    cookies_to_set[m.name] = m.value
    subrequest.cookies.update(cookies_to_set)
    context = context_factory(subrequest)
    subrequest.context = context
    return render_view_to_response(context, subrequest, name, secured)

def is_booster_cart_pred(context, request):
    return api.is_booster_cart(context.cart_setting)

def is_fc_cart_pred(context, request):
    return api.is_fc_cart(context.cart_setting)

def is_booster_or_fc_cart_pred(context, request):
    return api.is_booster_or_fc_cart(context.cart_setting)

coerce_extra_form_data = api.coerce_extra_form_data
