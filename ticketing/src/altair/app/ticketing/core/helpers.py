# -*- coding: utf-8 -*-
from datetime import datetime
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
            self.setting.cart_setting and self.setting.cart_setting.name or u'(名称なし)',
            ))

OrganizationSettingRenderer = SettingRendererWithCartSetting
EventSettingRenderer = SettingRendererWithCartSetting
