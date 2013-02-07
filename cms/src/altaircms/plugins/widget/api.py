import logging
logger = logging.getLogger(__name__)
from ..api import list_from_setting_value
from altaircms.plugins.api import get_widget_utility

def get_rendering_function_via_page(widget, bname, bsettings, type_=None):
    bsettings.need_extra_in_scan("request")
    bsettings.need_extra_in_scan("page")
    def closure():
        try:
            request = bsettings.extra["request"]
            page = bsettings.extra["page"]
            utility = get_widget_utility(request, page, type_ or widget.type)
            return utility.render_action(request, page, widget, bsettings)
        except Exception, e:
            logger.exception(str(e))
            _type = type_ or widget.type
            logger.warn("%s_merge_settings. info is empty" % _type)
            return u"%s widget: %s" % (_type, str(e))
    return closure


class DisplayTypeSelectRendering(object):
    def __init__(self, params, configparser):
        jnames = list_from_setting_value(params["jnames"].decode("utf-8"))
        self.names = names = list_from_setting_value(params["names"].decode("utf-8"))
        self.choices = zip(names, jnames)

        self.name_to_jname = dict(self.choices)
        self.jname_to_name = dict(zip(jnames, names))
        self.actions = {}

    def validation(self):
        return all(name in self.actions for name in self.names)

    def register(self, name, action):
        self.actions[name] = action

    def lookup(self, k, default=None):
        return self.actions.get(k, default)
