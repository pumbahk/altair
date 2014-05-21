# -*- coding: utf-8 -*-
from datetime import datetime
from pyramid.security import has_permission, ACLAllowed

from altair.app.ticketing.core.models import RefundStatusEnum

__all__ = [
    'build_sales_segment_list_for_inner_sales',
    'get_refund_status_label',
    ]

refund_status_labels = {
    RefundStatusEnum.Waiting.v: u'払戻予約',
    RefundStatusEnum.Refunding.v: u'払戻中',
    RefundStatusEnum.Refunded.v: u'払戻完了',
    }

def get_refund_status_label(status):
    return refund_status_labels.get(int(status), u'?')

def build_sales_segment_list_for_inner_sales(sales_segments, now=None, request=None):
    if now is None:
        now = datetime.now()
    def sales_segment_sort_key_func(ss):
        return (
            ss.kind == u'sales_counter',
            ss.start_at is None or ss.start_at <= now,
            ss.end_at is None or now <= ss.end_at,
            -ss.start_at.toordinal() if ss.start_at else 0,
            ss.id
            )
    if request and not isinstance(has_permission('event_editor', request.context, request), ACLAllowed):
        sales_segments = [ss for ss in sales_segments if ss.setting.sales_counter_selectable]
    return sorted(sales_segments, key=sales_segment_sort_key_func, reverse=True)
