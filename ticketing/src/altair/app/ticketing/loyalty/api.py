# encoding: utf-8
from decimal import Decimal

def applicable_point_grant_settings_for_product(product, now, type=None):
    return [
        point_grant_setting
        for point_grant_setting in product.point_grant_settings
        if point_grant_setting.applicable_to(now, type)
        ]

def get_defaults_for_organization(organization):
    setting = organization.setting
    defaults = {}
    if setting.point_type:
        defaults[setting.point_type] = dict(
            point_grant_setting=None,
            fixed=setting.point_fixed,
            rate=setting.point_rate
            )
    return defaults

def applicable_point_grant_settings_for_order(order, defaults=None):
    if defaults is None:
        defaults = get_defaults_for_organization(order.performance.event.organization)
    point_grant_settings_by_type = {}

    # まずは商品毎の設定をリストに追加
    for ordered_product in order.ordered_products:
        for point_grant_setting in applicable_point_grant_settings_for_product(ordered_product.product, order.created_at):
            point_grant_settings_for_ordered_product = point_grant_settings_by_type.get(point_grant_setting.type)
            if point_grant_settings_for_ordered_product is None:
                point_grant_settings_for_ordered_product = point_grant_settings_by_type[point_grant_setting.type] = {}
            point_grant_settings = point_grant_settings_for_ordered_product.get(ordered_product)
            if point_grant_settings is None:
                point_grant_settings = point_grant_settings_for_ordered_product[ordered_product] = []
            point_grant_settings.append(dict(
                point_grant_setting=point_grant_setting,
                fixed=point_grant_setting.fixed,
                rate=point_grant_setting.rate
                ))

    # デフォルトの設定をリストに追加
    for type, default in defaults.items():
        for ordered_product in order.ordered_products:
            point_grant_settings_for_ordered_product = point_grant_settings_by_type.get(type)
            if point_grant_settings_for_ordered_product is None:
                point_grant_settings_for_ordered_product = point_grant_settings_by_type[type] = {}
            if ordered_product not in point_grant_settings_for_ordered_product:
                point_grant_settings_for_ordered_product[ordered_product] = [default]

    return point_grant_settings_by_type

def calculate_point_for_order(order, defaults=None):
    q = Decimal('0') # FIXME: this must be determined by what currency is applicable to the order
    def calculate_point(point_grant_setting_dict, subtotal):
        return (
            (subtotal * Decimal(point_grant_setting_dict['rate']) if point_grant_setting_dict['rate'] is not None else Decimal()) + \
            (Decimal(point_grant_setting_dict['fixed']) if point_grant_setting_dict['fixed'] is not None else Decimal())
            ).quantize(q)

    retval = {}
    for type, point_grant_settings_by_type in applicable_point_grant_settings_for_order(order, defaults).items():
        point = Decimal()
        for ordered_product, point_grant_settings in point_grant_settings_by_type.items():
            subtotal = ordered_product.price * ordered_product.quantity
            point += sum(calculate_point(point_grant_setting, subtotal) for point_grant_setting in point_grant_settings)
        retval[type] = point

    return retval
