# -*- coding:utf-8 -*-

from altair.app.ticketing.i18n import custom_locale_negotiator

def _get_locale_name(request):
    return custom_locale_negotiator(request) if request.organization.setting.i18n else 'ja'

def get_delivery_method_info(request, dm, target):
    locale_name = _get_locale_name(request)
    if locale_name == 'ja' and hasattr(dm, target):
        return getattr(dm, target)
    elif locale_name in dm.preferences and target in dm.preferences[locale_name]:
        return dm.preferences[locale_name][target]
    elif hasattr(dm, target):
        return getattr(dm, target)

def get_payment_method_info(request, pm, target):
    locale_name = _get_locale_name(request)
    if locale_name == 'ja' and hasattr(pm, target):
        return getattr(pm, target)
    elif locale_name in pm.preferences and target in pm.preferences[locale_name]:
        return pm.preferences[locale_name][target]
    elif hasattr(pm, target):
        return getattr(pm, target)