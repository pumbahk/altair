# -*- coding:utf-8 -*-

import re
import itertools
from pyramid.decorator import reify
from pyramid.exceptions import ConfigurationError
from altaircms.plugins.helpers import get_installed_widgets, list_from_setting_value
from altaircms.auth.api import get_organization_mapping
from altaircms.auth.api import fetch_correct_organization
from zope.interface import implementer
from .interfaces import IConflictValidateFunction

import logging
logger = logging.getLogger(__file__)


"""
## in development.ini

altaircms.widget.settings =
   altaircms.plugins.widget:ticketstar.widget.settings.ini
   altaircms.plugins.widget:89ers.widget.settings.ini


## 以下のような.ini fileをorganizationの数だけ用意(e.g. ticketstar.widget.settings.ini)
## organization.nameはorganization.jsonの内容
[base]
organization.name = default-organization

dispatch_function = altaircms.plugins.api.page_type
dispatch_conds = 
   event_page
   other_page

[event_page]
widgets = 
   image
   heading
   ticketlist

[other_page]
widgets = 
   image
   heading

[image]
path = altaircms.plugins.widget.image
get_renderer = altaircms.plugins.widget.image.api:get_renderer

[ticketlist]
path = altaircms.plugins.widget.ticketlist
get_renderer = altaircms.plugins.widget.ticketlist.api:get_renderer

[heading]
path = altaircms.plugins.widget.heading
renderers = 
   ticketstar_heading1
   ticketstar_heading2
   ticketstar_heading3
get_renderer = altaircms.plugins.widget.image.api:get_renderer
"""

@implementer(IConflictValidateFunction)
def widget_conflict_validator(config, widgets):
    stored = get_installed_widgets(config.registry.settings).keys()
    for w in widgets:
        if not w in stored:
            raise ConfigurationError("`%s` is invalid widget name. not found in installed widgets(%s)" % (w,stored))    

## todo redefine
WIDGET_LABEL_DICT =  {
    "image": u"画像",
    "freetext": u"フリーテキスト",
    "flash" : u"flash",
    "movie" : u"動画",
    "calendar" : u"カレンダー",
    "ticketlist" : u"チケットリスト",
    "performancelist" : u"公演リスト",
    "menu" : u"メニュー",
    "summary" : u"サマリー",
    "iconset" : u"アイコンセット",
    "topic" : u"トピック",
    "breadcrumbs" : u"パンくずリスト",
    "countdown" : u"カウントダウン",
    "linklist" : u"リンクリスト",
    "heading" : u"見出し",
    "promotion" : u"プロモーション枠",
    "anchorlist" : u"ページ内リンク一覧",
    "purchase" : u"購入ボタン",
    "twitter" : u"twitter",
    "rawhtml" : u"rawhtml"
    }

class WidgetAggregator(object):
    @classmethod
    def from_target_config(cls, config, target_config, validator=None, configparser=None):
        widgets = list_from_setting_value(target_config["widgets"])
        if validator:
            validator(config, widgets)

        ## this is adhoc code.
        utilities = {}
        for k in widgets:
            if configparser.has_option(k, "utility"):
                utility_cls  = config.maybe_dotted(configparser.get(k, "utility"))
                utility_instance = utility_cls().parse_settings(config, configparser)
                if not hasattr(utility_instance, "validation") or utility_instance.validation():
                    utilities[k] = utility_instance
        logger.debug("*widget aggregator* widgets:%s,  utilities:%s" % (widgets, utilities))
        return cls(widgets, utilities=utilities)

    def __init__(self, widgets, utilities=None):
        self.widgets = widgets
        self.utilities = utilities or {}

    def get_widget_paletcode(self, request):
        fmt = u"""<div id="%s" class="widget float-left">%s</div>"""
        content = u"\n".join(fmt % (w, WIDGET_LABEL_DICT.get(w, u"名前未定")) 
                             for w in self.widgets)
        return u"""<div id="widget_palet">%s</div>""" % content

    def get_widget_jscode(self, request): #todo fix
        base = u"""<script type="text/javascript" src="/static/js/my/widgets/base.js"></script>"""
        fmt = u"""<script type="text/javascript" src="/plugins/static/js/widget/lib/%s.js"></script>"""
        return u"\n".join(itertools.chain([base], (fmt % w for w in self.widgets)))

    def get_widget_csscode(self, request):
        return u"\n".join(w.csscode(request) for w in self.widgets)

class WidgetAggregatorDispatcher(object):
    ## lookup:
    ## result_cont = self.dispatch_cont.get(organization)
    ## result_cont(request, page) => get aggregation object

    def __init__(self):
        self.conts = {}

    def add_dispatch_cont(self, key, dispatch_function, aggregators):
        after_dispatch = aggregators
        def dispatch(request, page):
            r = dispatch_function(request, page)
            logger.debug("widget aggretator subdispatch: %s" % r)
            return after_dispatch[r]

        ## for convinience
        dispatch._after_dispatch = after_dispatch
        logger.debug("widget aggregator add dispatch:%s <- %s" % (key, aggregators))
        self.conts[key] = dispatch

    def dispatch(self, request, page):
        ### !! request.`organizationかrequest.organization が取れること前提にしている　
        organization = fetch_correct_organization(request)
        assert organization.id == page.organization_id
        k = (organization.backend_id, organization.auth_source)

        logger.debug("widget aggregator dispach:%s" % (k,))
        subdispatch = self.conts[k]
        return subdispatch(request, page)


class WidgetAggregatorConfig(object):
    SPLIT_RX = re.compile("\s+")

    def __init__(self, config, configparser,
                 target_section="base", 
                 _organization_mapping=get_organization_mapping):
        self.config = config
        self.target_section = target_section
        self.configparser = configparser
        self.get_organization_mapping = _organization_mapping

    @reify
    def dispatch_function(self):
        function_string = self.configparser.get(self.target_section, "dispatch_function")
        return self.config.maybe_dotted(function_string)
        
    @reify
    def dispatch_conds(self):
        conds_string = self.configparser.get(self.target_section, "dispatch_conds")
        return list_from_setting_value(conds_string, rx=self.SPLIT_RX)

    @reify
    def organization_name(self):
        return self.configparser.get(self.target_section, "organization.name")

    @reify
    def get_keys(self):
        mapping = self.get_organization_mapping(self.config)
        return mapping.get_keypair(self.organization_name)

    def create_subdispatch_dict(self, config, validator=widget_conflict_validator):
        D = {}
        for k in self.dispatch_conds:
            D[k] = WidgetAggregator.from_target_config(config, dict(self.configparser.items(k)),
                                                       validator=validator, configparser=self.configparser)
        return D
