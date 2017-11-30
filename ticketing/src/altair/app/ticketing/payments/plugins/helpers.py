# -*- coding:utf-8 -*-

from altair.app.ticketing.i18n import custom_locale_negotiator

def _get_locale_name(request):
    return custom_locale_negotiator(request) if request.organization.setting.i18n else 'ja'

def delivery_method_get_description(request, dm):
    locale_name = _get_locale_name(request)
    if locale_name == 'ja' and hasattr(dm, 'description'):
        return getattr(dm, 'description')
    elif locale_name in dm.preferences and 'description' in dm.preferences[locale_name]:
        return dm.preferences[locale_name]['description']
    elif hasattr(dm, 'description'):
        return getattr(dm, 'description')

def payment_method_get_description(request, pm):
    locale_name = _get_locale_name(request)
    if locale_name == 'ja' and hasattr(pm, 'description'):
        return getattr(pm, 'description')
    elif locale_name in pm.preferences and 'description' in pm.preferences[locale_name]:
        return pm.preferences[locale_name]['description']
    elif hasattr(pm, 'description'):
        return getattr(pm, 'description')