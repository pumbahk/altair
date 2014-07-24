# -*- coding:utf-8 -*-

""" PC/Mobile のスーパービュークラス
"""
import logging
from pyramid.httpexceptions import HTTPFound
from pyramid.decorator import reify
from sqlalchemy.sql.expression import desc, asc
from sqlalchemy.orm import joinedload, aliased
from altair.app.ticketing.core import models as c_models
from altair.sqlahelper import get_db_session
from altair.mobile.interfaces import IMobileRequest
from altair.formhelpers.form import OurDynamicForm
from altair.formhelpers import widgets
from altair.formhelpers import fields
from altair.formhelpers.filters import text_type_but_none_if_not_given
from altair.formhelpers.validators import Required
from wtforms.validators import Optional
from altair.formhelpers.translations import Translations
from . import helpers as h
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
from .interfaces import ICartContext

logger = logging.getLogger(__name__)

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
            performance_id = self.request.context.performance.id
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

    if ICartContext.providedBy(request.context):
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

        stocks = stocks_for_stock_type.get(stock_type.id)
        if stocks is None:
            stocks = stocks_for_stock_type[stock_type.id] = []
        stocks.append(stock)

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
        product_dicts = []
        min_product_quantity = stock_type.min_product_quantity
        max_product_quantity = stock_type.max_product_quantity
        min_quantity = stock_type.min_quantity
        max_quantity = stock_type.max_quantity

        total_quantity_per_stock_type = 0
        for target_stock in set(stocks_for_stock_type[stock_type.id]):
            total_quantity_per_stock_type = total_quantity_per_stock_type + target_stock.quantity

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
            actual_availability_for_stock_type = max(actual_availability_for_stock_type, actual_availability)

            product_dicts.append(
                dict(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    price=h.format_number(product.price, ","), 
                    detail=h.product_name_with_unit(product_items_for_product[product.id]),
                    unit_template=h.build_unit_template(product_items_for_product[product.id]),
                    quantity_power=quantity_power,
                    max_quantity=max_product_quantity_per_product,
                    max_product_quatity=max_product_quatity,
                    min_product_quantity_from_product=product.min_product_quantity,
                    max_product_quantity_from_product=product.max_product_quantity,
                    min_product_quantity_per_product=min_product_quantity_per_product,
                    max_product_quantity_per_product=max_product_quantity_per_product,
                    elements=dict(
                        (
                            product_item.stock_id,
                            dict(
                                quantity=product_item.quantity,
                                is_primary_seat_stock_type=(stock_for_product_item[product_item.id].stock_type_id == product.seat_stock_type_id),
                                is_seat_stock_type=(not stock_types[stock_for_product_item[product_item.id].stock_type_id].quantity_only)
                                )
                            )
                        for product_item in product_items_for_product[product.id]
                        )
                    )
                )

        event = sales_segment.performance.event
        retval.append(dict(
            id=stock_type.id,
            name=stock_type.name,
            description=stock_type.description,
            style=stock_type.style,
            stocks=[st.id for st in stocks_for_stock_type[stock_type.id]],
            availability=availability_for_stock_type,
            actual_availability=actual_availability_for_stock_type,
            availability_text=h.get_availability_text(actual_availability_for_stock_type, total_quantity_per_stock_type, event.setting.middle_stock_threshold, event.setting.middle_stock_threshold_percent),
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
        if product.min_product_quantity is not None and \
           quantity < product.min_product_quantity:
            raise PerProductProductQuantityOutOfBoundsError(
                quantity,
                product.min_product_quantity,
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

    def _convert_choices(self, choice_descs):
        return [(choice_desc['value'], choice_desc['label']) for choice_desc in choice_descs]

    def _build_validators(self, field_desc):
        validators = []
        if field_desc['required']:
            validators.append(Required())
        else:
            validators.append(Optional())
        return validators

    def _build_text(self, field_desc):
        return fields.OurTextField(
            label=field_desc['display_name'],
            validators=self._build_validators(field_desc)
            )

    def _build_textarea(self, field_desc):
        return fields.OurTextAreaField(
            label=field_desc['display_name'],
            validators=self._build_validators(field_desc)
            )

    def _build_select(self, field_desc):
        return fields.OurSelectField(
            label=field_desc['display_name'],
            validators=self._build_validators(field_desc),
            choices=self._convert_choices(field_desc['choices'])
            )

    def _build_multiple_select(self, field_desc):
        return fields.OurSelectMultipleField(
            label=field_desc['display_name'],
            validators=self._build_validators(field_desc),
            choices=self._convert_choices(field_desc['choices'])
            )

    def _build_radio(self, field_desc):
        return fields.OurRadioField(
            label=field_desc['display_name'],
            validators=self._build_validators(field_desc),
            choices=self._convert_choices(field_desc['choices']),
            coerce=text_type_but_none_if_not_given
            )

    def _build_checkbox(self, field_desc):
        return fields.OurSelectMultipleField(
            label=field_desc['display_name'],
            validators=self._build_validators(field_desc),
            choices=self._convert_choices(field_desc['choices']),
            widget=widgets.CheckboxMultipleSelect(
                multiple=True,
                outer_html_tag='ul',
                inner_html_tag='li'
                )
            )


    field_factories = {
        u'text': _build_text,
        u'textarea': _build_textarea,
        u'select': _build_select,
        u'multiple_select': _build_multiple_select,
        u'radio': _build_radio,
        u'checkbox': _build_checkbox,
        }

    def __call__(self, request, extra_form_fields, formdata=None):
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
        form = OurDynamicForm(
            formdata=formdata,
            _fields=unbound_fields,
            _translations=Translations(),
            name_builder=lambda name: u'extra_field[%s]' % name
            )
        fields = []
        for field_desc in extra_form_fields:
            field = None
            try:
                field = form[field_desc['name']]
            except KeyError:
                pass
            fields.append({
                'description': field_desc['description'],
                'note': field_desc['note'],
                'required': field_desc['required'],
                'field': field,
                })
        return form, fields

build_dynamic_form = DynamicFormBuilder()

def get_extra_form_data_pair_pairs(request, sales_segment, data):
    extra_form_fields = sales_segment.setting.extra_form_fields
    if extra_form_fields is None:
        return []
    retval = []
    for field_desc in extra_form_fields:
        if field_desc['kind'] == 'description_only':
            continue
        field_value = data.get(field_desc['name'])
        display_value = None
        if field_desc['kind'] in ('text', 'textarea'):
            display_value = field_value
        elif field_desc['kind'] in ('select', 'radio'):
            v = [pair for pair in field_desc['choices'] if pair['value'] == field_value]
            if len(v) > 0:
                display_value = v[0]['label']
            else:
                display_value = field_value
        elif field_desc['kind'] in ('multiple_select', 'checkbox'):
            display_value = []
            for c in field_value:
                v = [pair for pair in field_desc['choices'] if pair['value'] == c]
                if len(v) > 0:
                    v = v[0]['label']
                else:
                    v = c
                display_value.append(v)
        else:
            logger.warning('unsupported kind: %s' % field_desc['kind'])
            display_value = field_value

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
