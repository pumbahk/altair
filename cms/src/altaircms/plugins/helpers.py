import re
from pyramid.exceptions import ConfigurationError

WIDGETKEY = "_widgets"
def get_installed_widgets(settings):
    return settings.get(WIDGETKEY, {})

def add_widgetname(config, widgetname, value=None):
    settings = config.registry.settings
    if WIDGETKEY not in settings:
        settings[WIDGETKEY] = {}
    if widgetname in settings[WIDGETKEY]:
        raise ConfigurationError("`%s` is conflicted as widget names. (%s)" % (widgetname, settings[WIDGETKEY]))
    settings[WIDGETKEY][widgetname] = value or widgetname


SPLIT_RX = re.compile("\s+")

def list_from_setting_value(value, rx=SPLIT_RX):
    return [e for e in (x.strip() for x in rx.split(value)) if e]


