# -*- coding: utf-8 -*-
from datetime import datetime
from pyramid.security import has_permission, ACLAllowed
from sqlalchemy.orm.properties import RelationshipProperty
from zope.interface import implementer
from markupsafe import Markup, escape
from altair.saannotation import get_annotations_for

from altair.app.ticketing.core.models import RefundStatusEnum
from altair.app.ticketing.core.interfaces import ISettingRenderer

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

@implementer(ISettingRenderer)
class DefaultSettingRenderer(object):
    def __init__(self, setting):
        self.setting = setting

    def render_default(self, request, v):
        return v

    def get_iter(self, request):
        for prop in self.setting.__mapper__.iterate_properties:
            if isinstance(prop, RelationshipProperty):
                continue
            annotations = get_annotations_for(prop)
            if annotations and annotations.get('visible_column') and hasattr(self.setting, prop.key):
                renderer = '_render_%s' % prop.key
                v = getattr(self.setting, prop.key, None)
                if hasattr(self, renderer):
                    rv = getattr(self, renderer)(request, prop.key, v)
                else:
                    rv = self.render_default(request, v)
                yield (prop.key, v), (annotations.get('label') or prop.key, rv)

@implementer(ISettingRenderer)
class SettingRendererWithCartSetting(DefaultSettingRenderer):
    def _render_cart_setting_id(self, request, k, v):
        return Markup(u'<a href="%s">%s</a>' % (
            request.route_path('cart_setting.index'),
            self.setting.cart_setting.name or u'(名称なし)',
            ))

OrganizationSettingRenderer = SettingRendererWithCartSetting
EventSettingRenderer = SettingRendererWithCartSetting
