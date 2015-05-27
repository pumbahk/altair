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

    def format_issuing_start_at(self, pdmp):
        if pdmp.issuing_start_day_calculation_base == DateCalculationBase.Absolute.v:
            if pdmp.issuing_start_at is not None:
                return create_date_time_formatter(self.request).format_datetime(pdmp.issuing_start_at, with_weekday=True)
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.OrderDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'購入日'
                elif pdmp.issuing_interval_days > 0:
                    return u'購入から%d日後' % pdmp.issuing_interval_days
                else:
                    return u'不正な値'
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.OrderDateTime.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'購入日時'
                elif pdmp.issuing_interval_days > 0:
                    return u'購入日時から%d日後' % pdmp.issuing_interval_days
                else:
                    return u'不正な値'
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.PerformanceStartDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'公演開始日'
                elif pdmp.issuing_interval_days > 0:
                    return u'公演開始から%d日後' % pdmp.issuing_interval_days
                elif pdmp.issuing_interval_days < 0:
                    return u'公演開始の%d日前' % -pdmp.issuing_interval_days
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.PerformanceEndDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'公演終了日'
                elif pdmp.issuing_interval_days > 0:
                    return u'公演終了から%d日後' % pdmp.issuing_interval_days
                elif pdmp.issuing_interval_days < 0:
                    return u'公演終了の%d日前' % -pdmp.issuing_interval_days
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.SalesStartDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'販売開始日'
                elif pdmp.issuing_interval_days > 0:
                    return u'販売開始から%d日後' % pdmp.issuing_interval_days
                elif pdmp.issuing_interval_days < 0:
                    return u'販売開始の%d日前' % -pdmp.issuing_interval_days
        elif pdmp.issuing_start_day_calculation_base == DateCalculationBase.SalesEndDate.v:
            if pdmp.issuing_interval_days is not None:
                if pdmp.issuing_interval_days == 0:
                    return u'販売終了日'
                elif pdmp.issuing_interval_days > 0:
                    return u'販売終了から%d日後' % pdmp.issuing_interval_days
                elif pdmp.issuing_interval_days < 0:
                    return u'販売終了の%d日前' % -pdmp.issuing_interval_days
        return u'未設定'

    def format_issuing_end_at(self, pdmp):
        if pdmp.issuing_end_day_calculation_base == DateCalculationBase.Absolute.v:
            if pdmp.issuing_end_at is not None:
                return create_date_time_formatter(self.request).format_datetime(pdmp.issuing_end_at, with_weekday=True)
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.OrderDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'購入日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'購入から%d日後' % pdmp.issuing_end_in_days
                else:
                    return u'不正な値'
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.OrderDateTime.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'購入日時'
                elif pdmp.issuing_end_in_days > 0:
                    return u'購入日時から%d日後' % pdmp.issuing_end_in_days
                else:
                    return u'不正な値'
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.PerformanceStartDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'公演開始日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'公演開始から%d日後' % pdmp.issuing_end_in_days
                elif pdmp.issuing_end_in_days < 0:
                    return u'公演開始の%d日前' % -pdmp.issuing_end_in_days
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.PerformanceEndDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'公演終了日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'公演終了から%d日後' % pdmp.issuing_end_in_days
                elif pdmp.issuing_end_in_days < 0:
                    return u'公演終了の%d日前' % -pdmp.issuing_end_in_days
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.SalesStartDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'販売開始日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'販売開始から%d日後' % pdmp.issuing_end_in_days
                elif pdmp.issuing_end_in_days < 0:
                    return u'販売開始の%d日前' % -pdmp.issuing_end_in_days
        elif pdmp.issuing_end_day_calculation_base == DateCalculationBase.SalesEndDate.v:
            if pdmp.issuing_end_in_days is not None:
                if pdmp.issuing_end_in_days == 0:
                    return u'販売終了日'
                elif pdmp.issuing_end_in_days > 0:
                    return u'販売終了から%d日後' % pdmp.issuing_end_in_days
                elif pdmp.issuing_end_in_days < 0:
                    return u'販売終了の%d日前' % -pdmp.issuing_end_in_days
        return u'未設定'

    def format_payment_start_at(self, pdmp):
        if pdmp.payment_start_day_calculation_base == DateCalculationBase.Absolute.v:
            if pdmp.payment_start_at is not None:
                return create_date_time_formatter(self.request).format_datetime(pdmp.payment_start_at, with_weekday=True)
        elif pdmp.payment_start_day_calculation_base == DateCalculationBase.OrderDate.v:
            if pdmp.payment_start_in_days is not None:
                if pdmp.payment_start_in_days == 0:
                    return u'購入日'
                elif pdmp.payment_start_in_days > 0:
                    return u'購入から%d日後' % pdmp.payment_start_in_days
                else:
                    return u'不正な値'
        elif pdmp.payment_start_day_calculation_base == DateCalculationBase.OrderDateTime.v:
            if pdmp.payment_start_in_days is not None:
                if pdmp.payment_start_in_days == 0:
                    return u'購入日時'
                elif pdmp.payment_start_in_days > 0:
                    return u'購入日時から%d日後' % pdmp.payment_start_in_days
                else:
                    return u'不正な値'
        elif pdmp.payment_start_day_calculation_base == DateCalculationBase.PerformanceStartDate.v:
            if pdmp.payment_start_in_days is not None:
                if pdmp.payment_start_in_days == 0:
                    return u'公演開始日'
                elif pdmp.payment_start_in_days > 0:
                    return u'公演開始から%d日後' % pdmp.payment_start_in_days
                elif pdmp.payment_start_in_days < 0:
                    return u'公演開始の%d日前' % -pdmp.payment_start_in_days
        elif pdmp.payment_start_day_calculation_base == DateCalculationBase.PerformanceEndDate.v:
            if pdmp.payment_start_in_days is not None:
                if pdmp.payment_start_in_days == 0:
                    return u'公演終了日'
                elif pdmp.payment_start_in_days > 0:
                    return u'公演終了から%d日後' % pdmp.payment_start_in_days
                elif pdmp.payment_start_in_days < 0:
                    return u'公演終了の%d日前' % -pdmp.payment_start_in_days
        elif pdmp.payment_start_day_calculation_base == DateCalculationBase.SalesStartDate.v:
            if pdmp.payment_start_in_days is not None:
                if pdmp.payment_start_in_days == 0:
                    return u'販売開始日'
                elif pdmp.payment_start_in_days > 0:
                    return u'販売開始から%d日後' % pdmp.payment_start_in_days
                elif pdmp.payment_start_in_days < 0:
                    return u'販売開始の%d日前' % -pdmp.payment_start_in_days
        elif pdmp.payment_start_day_calculation_base == DateCalculationBase.SalesEndDate.v:
            if pdmp.payment_start_in_days is not None:
                if pdmp.payment_start_in_days == 0:
                    return u'販売終了日'
                elif pdmp.payment_start_in_days > 0:
                    return u'販売終了から%d日後' % pdmp.payment_start_in_days
                elif pdmp.payment_start_in_days < 0:
                    return u'販売終了の%d日前' % -pdmp.payment_start_in_days
        return u'未設定'

    def format_payment_due_at(self, pdmp):
        if pdmp.payment_due_day_calculation_base == DateCalculationBase.Absolute.v:
            if pdmp.payment_due_at is not None:
                return create_date_time_formatter(self.request).format_datetime(pdmp.payment_due_at, with_weekday=True)
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.OrderDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'購入日'
                elif pdmp.payment_period_days > 0:
                    return u'購入から%d日後' % pdmp.payment_period_days
                else:
                    return u'不正な値'
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.OrderDateTime.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'購入日時'
                elif pdmp.payment_period_days > 0:
                    return u'購入日時から%d日後' % pdmp.payment_period_days
                else:
                    return u'不正な値'
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.PerformanceStartDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'公演開始日'
                elif pdmp.payment_period_days > 0:
                    return u'公演開始から%d日後' % pdmp.payment_period_days
                elif pdmp.payment_period_days < 0:
                    return u'公演開始の%d日前' % -pdmp.payment_period_days
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.PerformanceEndDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'公演終了日'
                elif pdmp.payment_period_days > 0:
                    return u'公演終了から%d日後' % pdmp.payment_period_days
                elif pdmp.payment_period_days < 0:
                    return u'公演終了の%d日前' % -pdmp.payment_period_days
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.SalesStartDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'販売開始日'
                elif pdmp.payment_period_days > 0:
                    return u'販売開始から%d日後' % pdmp.payment_period_days
                elif pdmp.payment_period_days < 0:
                    return u'販売開始の%d日前' % -pdmp.payment_period_days
        elif pdmp.payment_due_day_calculation_base == DateCalculationBase.SalesEndDate.v:
            if pdmp.payment_period_days is not None:
                if pdmp.payment_period_days == 0:
                    return u'販売終了日'
                elif pdmp.payment_period_days > 0:
                    return u'販売終了から%d日後' % pdmp.payment_period_days
                elif pdmp.payment_period_days < 0:
                    return u'販売終了の%d日前' % -pdmp.payment_period_days
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
