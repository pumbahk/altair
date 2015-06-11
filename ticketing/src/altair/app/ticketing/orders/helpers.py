# encoding: utf-8
from altair.app.ticketing.orders.models import (
    ImportStatusEnum,
    ImportTypeEnum,
    AllocationModeEnum,
    OrderImportTask,
    ProtoOrder,
    orders_seat_table,
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    orders_seat_table,
    )
from sqlalchemy import sql
from altair.app.ticketing.core import models as c_models
from markupsafe import Markup

def build_candidate_id(token, seat, ordered_product_item, ticket):
    #token.id@seat@ordered_product_item.id@ticket.id
    return unicode(token.id if token else None) + u"@" + unicode(seat.id if seat else None) + u"@" + unicode(ordered_product_item.id) + u"@" + unicode(ticket.id)

def decode_candidate_id(candidate_id):
    #token@seat@ordered_product_item.id@ticket.id
    return tuple((None if e == "None" else unicode(e)) for e in candidate_id.split("@"))

import_type_labels = {
    ImportTypeEnum.Create.v: u'新規登録',
    ImportTypeEnum.Update.v: u'予約を更新',
    ImportTypeEnum.Create.v | ImportTypeEnum.Update.v: u'予約の更新と登録を同時に行う',
    }

allocation_mode_labels = {
    AllocationModeEnum.AlwaysAllocateNew.v: u'座席番号を無視し常に自動配席する',
    AllocationModeEnum.NoAutoAllocation.v: u'座席番号に該当する座席を配席する',
    }

import_status_labels = {
    ImportStatusEnum.Waiting.v: u'インポート待ち',
    ImportStatusEnum.Importing.v: u'インポート中',
    ImportStatusEnum.Imported.v: u'インポート完了',
    ImportStatusEnum.Aborted.v: u'インポート異常終了',
    }

def get_import_type_label(import_type, no_option_desc=False):
    import_type = int(import_type)
    s = import_type_labels.get(import_type & (ImportTypeEnum.Create.v | ImportTypeEnum.Update.v))
    if s is None:
        return u'?'
    if no_option_desc or (import_type & ImportTypeEnum.Create.v) == 0:
        return s
    if import_type & ImportTypeEnum.AlwaysIssueOrderNo.v != 0:
        how_to_issue_order_no = u'常に新しい予約番号を発番'
    else:
        how_to_issue_order_no = u'予約番号を再利用'
    return u'%s (%s)' % (s, how_to_issue_order_no)

def get_allocation_mode_label(allocation_mode):
    return allocation_mode_labels.get(int(allocation_mode), u'?')

def get_order_import_task_status_label(status):
    return import_status_labels.get(int(status), u'?')

def get_merge_order_attributes_label(yesno):
    return u'更新' if yesno else u'置換'

def order_import_task_stats(task):
    from altair.app.ticketing.models import DBSession as session
    stats = dict()

    # インポート方法
    stats['import_type'] = get_import_type_label(task.import_type)
    # 配席モード
    stats['allocation_mode'] = get_allocation_mode_label(task.allocation_mode)
    # 購入情報属性のマージ
    stats['merge_order_attributes'] = get_merge_order_attributes_label(task.merge_order_attributes)

    def none_to_zero(x):
        return [i or 0 for i in x]

    def build_counts_dict(filter_fn):
        return {
            'order_count': \
                none_to_zero(filter_fn(
                    session.query(ProtoOrder) \
                    .filter(ProtoOrder.order_import_task_id == task.id)
                    ) \
                .with_entities(sql.func.count(ProtoOrder.id), sql.func.sum(ProtoOrder.processed_at != None)) \
                .one()),
            'seat_count': \
                none_to_zero(filter_fn(
                    session.query(ProtoOrder) \
                    .join(ProtoOrder.items) \
                    .join(OrderedProduct.elements) \
                    .outerjoin(OrderedProductItem.seats) \
                    .filter(ProtoOrder.order_import_task_id == task.id)
                    ) \
                .with_entities(sql.func.count(c_models.Seat.id), sql.func.sum(ProtoOrder.processed_at != None)) \
                .one()),
            'count_per_product': dict(
                filter_fn(session.query(ProtoOrder) \
                    .join(ProtoOrder.items) \
                    .join(OrderedProduct.elements) \
                    .join(OrderedProduct.product) \
                    .outerjoin(OrderedProductItem.tokens) \
                    .group_by(c_models.Product.id) \
                    .filter(ProtoOrder.order_import_task_id == task.id)
                    ) \
                .with_entities(c_models.Product, sql.func.count(sql.func.distinct(OrderedProductItemToken.id))) \
                ),
            'count_per_pdmp': dict(
                (pdmp, (order_count, seat_count))
                for pdmp, order_count, seat_count in
                    filter_fn(session.query(ProtoOrder) \
                        .join(ProtoOrder.items) \
                        .join(ProtoOrder.payment_delivery_pair) \
                        .join(OrderedProduct.elements) \
                        .outerjoin(OrderedProductItem.tokens) \
                        .group_by(c_models.PaymentDeliveryMethodPair.id) \
                        .with_entities(c_models.PaymentDeliveryMethodPair, sql.func.count(sql.func.distinct(ProtoOrder.id)), sql.func.count(sql.func.distinct(OrderedProductItemToken.id)))
                        .filter(ProtoOrder.order_import_task_id == task.id))
                ),
            }

    stats['import'] = build_counts_dict(lambda q: q.filter(ProtoOrder.original_order_id == None))
    stats['update'] = build_counts_dict(lambda q: q.filter(ProtoOrder.original_order_id != None))

    # OrderImportTaskからの情報
    stats['task_id'] = task.id
    stats['created_at'] = task.created_at
    stats['updated_at'] = task.updated_at
    stats['operator_name'] = task.operator.name
    stats['status'] = get_order_import_task_status_label(task.status)

    return stats

def error_level_to_html(request, error_level):
    from .importer import (IMPORT_ERROR, IMPORT_WARNING)
    label = u''
    style = u''
    if error_level > IMPORT_WARNING:
        label = u'エラー'
        style = u'label-important'
    else:
        label = u'警告'
        style = u'label-warning'
    return Markup(
        u'<span class="label {style}">{label}</span>'.format(
            style=style,
            label=label
            )
        )

def cancel_reason(reason):
    from .models import OrderCancelReasonEnum
    for e in OrderCancelReasonEnum:
        if e.v[0] == reason:
            return e.v[1]
    return u'?'
