# encoding: utf-8

import json as json_
from markupsafe import Markup
from pyramid.security import has_permission as security_has_permission
from pyramid.security import ACLAllowed
from webhelpers.util import html_escape

from altair.viewhelpers.datetime_ import (
    create_date_time_formatter,
    DateTimeHelper,
    )

from altair.app.ticketing.core.models import DateCalculationBase
from altair.app.ticketing.orders.models import OrderCancelReasonEnum
from altair.app.ticketing.core.interfaces import ISettingRenderer
from altair.app.ticketing.permissions.utils import RouteConfig, PermissionCategory
from altair.app.ticketing.fanstatic import get_resource_url


def render_label(label_text, label_type=None):
    if not label_text:
        return u''
    classes = [u'label']
    if label_type is not None:
        classes.append(u'label-%s' % label_type)
    return Markup(u'<span class="%s">%s</span>' % (
        u' '.join(classes), label_text))

def json(dict_):
    return json_.dumps(dict_)

class AdminHelperAdapter(object):
    def __init__(self, request):
        self.request = request

    def payment_status_string(self, order):
        label_text = None

        if order is None:
            pass
        elif order.payment_status == 'refunded' and order.cancel_reason == str(OrderCancelReasonEnum.CallOff.v[0]):
            label_text = u'払戻済み(中止)'
        elif order.payment_status == 'refunded':
            label_text = u'払戻済み'
        elif order.payment_status == 'refunding' and order.cancel_reason == str(OrderCancelReasonEnum.CallOff.v[0]):
            label_text = u'払戻予約(中止)'
        elif order.payment_status == 'refunding':
            label_text = u'払戻予約'
        elif order.payment_status == 'paid':
            label_text = u'入金済み'
        else:
            label_text = u'未入金'

        return label_text

    def payment_status_style(self, order):
        label_type = None

        if order is None:
            pass
        if order.payment_status == 'refunded':
            label_type = 'important'
        if order.payment_status == 'refunding':
            label_type = 'warning'
        elif order.payment_status == 'paid':
            label_type = 'success'
        else:
            label_type = 'inverse'
        return label_type

    def payment_status(self, order):
        return render_label(
            self.payment_status_string(order),
            self.payment_status_style(order))

    def delivery_status_string(self, order):
        if order is None:
            return None
        elif order.delivered_at:
            return u'配送済み'
        else:
            return u'未配送'

    def delivery_status_style(self, order):
        if order is None:
            return None
        elif order.delivered_at:
            return u'success'
        else:
            return u'inverse'

    def delivery_status(self, order):
        return render_label(
            self.delivery_status_string(order),
            self.delivery_status_style(order))

    def order_status_string(self, order):
        if order is None:
            pass
        elif order.status == 'canceled':
            return u'キャンセル'
        elif order.status == 'delivered':
            return u'配送済み'
        elif order.status == 'ordered':
            return u'受付済み'
        return None

    def order_status_style(self, order):
        if order is None:
            pass
        elif order.status == 'canceled':
            return u'important'
        elif order.status == 'delivered':
            return u'success'
        elif order.status == 'ordered':
            return u'warning'
        return None

    def order_status(self, order):
        return render_label(
            self.order_status_string(order),
            self.order_status_style(order))

    def order_resale_status(self, order):
        if order.has_resale_requests:
            return render_label(
                u"リセール情報あり",
                u'info'
            )
        else:
            return ""

    def ordered_product_item_token_resale_status(self, ordered_product_time_token):
        resale_request = ordered_product_time_token.resale_request
        if not resale_request:
            return ""
        else:
            return render_label(
                resale_request.verbose_status,
                resale_request.label_attribute
            )

    def has_permission(self, permission):
        return isinstance(
            security_has_permission(
                permission, self.request.context, self.request),
            ACLAllowed
            )

    def action_button(self, actions, order=None, vertical=True, options=None, dropup=False, align=None, extra_classes=None):
        count = 0
        if order is None:
            order = actions.keys()

        def attrs_str():
            attrs = actions[key].get('attrs', {})
            attrs['class'] = attrs.get('class', u'')
            if count == 0 or not vertical:
                attrs['class'] += u' ' + u'btn'
            if key == 'delete':
                attrs['data-controls-modal'] = u'modal-delete'
                attrs['data-backdrop'] = u'true'
                attrs['data-keyboard'] = u'true'
            if options is not None:
                attrs['class'] += u' ' + options
            if extra_classes:
                attrs['class'] += u' ' + u' '.join(extra_classes)
            return ' '.join(u'%s="%s"' % (name, html_escape(value)) for name, value in attrs.iteritems())

        html = []
        btn_group_class = 'dropup' if dropup else ''
        html.append(u'<div class="btn-group {}">'.format(btn_group_class))
        route_permission = self.request.route_permission
        if route_permission:
            count = 0
            for key in order:
                if key == 'divider':
                    html.append(u'<li class="divider"></li>')
                    continue
                if 'route_name' in actions[key]:
                    permissions = route_permission.get(actions[key]['route_name'])
                    if isinstance(permissions, basestring):
                        permissions = [permissions]
                    allowed = any(p and self.has_permission(p) for p in permissions)
                else:
                    allowed = True

                if not allowed:
                    return u''

                if vertical and count == 1:
                    html.append(u'<button class="btn%s dropdown-toggle" data-toggle="dropdown">' % (u' ' + u' '.join(extra_classes) if extra_classes else u''))
                    html.append(u'<span class="caret"></span>')
                    html.append(u'</button>')
                    dropdown_menu_class = ''
                    if align == 'right':
                        dropdown_menu_class = 'pull-right'
                    html.append(u'<ul class="dropdown-menu {}">'.format(dropdown_menu_class))
                if vertical and count > 0:
                    html.append(u'<li>')
                html.append(u'<a href="%s" %s>' % (html_escape(actions[key]['url']), attrs_str()))
                html.append(u'<i class="%s"></i> %s' % (html_escape(actions[key]['icon']), html_escape(actions[key]['label'])))
                html.append(u'</a>')
                if vertical and count > 0:
                    html.append(u'</li>')
                count += 1
            if vertical and count > 0:
                html.append(u'</ul>')
        html.append(u'</div>')

        return Markup(u''.join(html))

    def route_label(self, route_name):
        return RouteConfig.label(route_name)

    def permission_label(self, permission):
        return PermissionCategory.label(permission)

    def permissions(self):
        return PermissionCategory.items()

    DATE_CALCULATION_BASE_TRANSL = {
        DateCalculationBase.OrderDate.v: u'購入',
        DateCalculationBase.OrderDateTime.v: u'購入日時',
        DateCalculationBase.PerformanceStartDate.v: u'公演開始',
        DateCalculationBase.PerformanceEndDate.v: u'公演終了',
        DateCalculationBase.SalesStartDate.v: u'販売開始',
        DateCalculationBase.SalesEndDate.v: u'販売終了',
    }

    def _strf_relative_datetime(self, calc_base, days, time=None):
        """相対指定日時をフォーマットします。"""
        val = self.DATE_CALCULATION_BASE_TRANSL.get(calc_base)
        if not val:
            return u'不正な値'

        if days == 0:
            if calc_base != DateCalculationBase.OrderDateTime.v:
                val += u'日'
            # 購入日時は相対指定時間を持たない
            return u'{0}の{1:d}:{2:02d}'.format(val, time.hour, time.minute) \
                if calc_base != DateCalculationBase.OrderDateTime.v and time is not None else val
        elif days > 0:
            val += u'から{0:d}日後'.format(days)
            # 購入日時は相対指定時間を持たない
            return u'{0}の{1:d}:{2:02d}'.format(val, time.hour, time.minute) \
                if calc_base != DateCalculationBase.OrderDateTime.v and time is not None else val
        elif days < 0 and calc_base in \
                (DateCalculationBase.PerformanceStartDate.v, DateCalculationBase.PerformanceEndDate.v,
                 DateCalculationBase.SalesStartDate.v, DateCalculationBase.SalesEndDate.v):
            # 公演開始、公演終了、販売開始、販売終了は0未満を許可します
            val += u'の{0:d}日前'.format(-days)
            return u'{0}の{1:d}:{2:02d}'.format(val, time.hour, time.minute) \
                if time is not None else val

        return u'不正な値'

    def format_issuing_start_at(self, pdmp):
        # 絶対指定
        if pdmp.issuing_start_day_calculation_base == DateCalculationBase.Absolute.v and \
                pdmp.issuing_start_at is not None:
            return create_date_time_formatter(self.request).format_datetime(pdmp.issuing_start_at, with_weekday=True)
        # 相対指定
        elif pdmp.issuing_interval_days is not None:
            return self._strf_relative_datetime(
                pdmp.issuing_start_day_calculation_base, pdmp.issuing_interval_days, pdmp.issuing_interval_time)
        return u'未設定'

    def format_issuing_end_at(self, pdmp):
        # 絶対指定
        if pdmp.issuing_end_day_calculation_base == DateCalculationBase.Absolute.v and \
                pdmp.issuing_end_at is not None:
            return create_date_time_formatter(self.request).format_datetime(pdmp.issuing_end_at, with_weekday=True)
        # 相対指定
        elif pdmp.issuing_end_in_days is not None:
            return self._strf_relative_datetime(
                pdmp.issuing_end_day_calculation_base, pdmp.issuing_end_in_days, pdmp.issuing_end_in_time)
        return u'未設定'

    def format_payment_start_at(self, pdmp):
        # 絶対指定
        if pdmp.payment_start_day_calculation_base == DateCalculationBase.Absolute.v and \
                pdmp.payment_start_at is not None:
            return create_date_time_formatter(self.request).format_datetime(pdmp.payment_start_at, with_weekday=True)
        # 相対指定
        elif pdmp.payment_start_in_days is not None:
            return self._strf_relative_datetime(
                pdmp.payment_start_day_calculation_base, pdmp.payment_start_in_days)
        return u'未設定'

    def format_payment_due_at(self, pdmp):
        # 絶対指定
        if pdmp.payment_due_day_calculation_base == DateCalculationBase.Absolute.v and \
                pdmp.payment_due_at is not None:
            return create_date_time_formatter(self.request).format_datetime(pdmp.payment_due_at, with_weekday=True)
        # 相対指定
        elif pdmp.payment_period_days is not None:
            return self._strf_relative_datetime(
                pdmp.payment_due_day_calculation_base, pdmp.payment_period_days, pdmp.payment_period_time)
        return u'未設定'

    def fanstatic_resource_url(self, resource):
        return get_resource_url(self.request, resource)

    def describe_iter(self, setting, renderer_name=''):
        from altair.app.ticketing.core.helpers import DefaultSettingRenderer
        setting_renderer = self.request.registry.queryAdapter(setting, ISettingRenderer, name=renderer_name)
        if setting_renderer is None:
            setting_renderer = DefaultSettingRenderer(setting)
        return setting_renderer.get_iter(self.request)

    def auth_type_label(self, auth_type):
        from altair.app.ticketing.security import get_display_name
        return get_display_name(self.request, auth_type)
