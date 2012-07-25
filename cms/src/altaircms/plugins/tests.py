# -*- coding:utf-8 -*-

from ConfigParser import SafeConfigParser
from StringIO import StringIO
import unittest
from pyramid import testing

class DummyOpen(object):
    def __init__(self, string, name=None):
        self.buf = StringIO(string.encode("utf-8"))
        self.buf.name = name
        self._called = []

    def __enter__(self, *args, **kwargs):
        self._called.append("enter")
        return self.buf

    def __exit__(self, *args, **kwargs):
        self._called.append("exit")

def make_config(name, content):
    buf = DummyOpen(content, name).buf
    config = SafeConfigParser()
    config.readfp(buf)        
    return config

def dummy_mapping_utility(request_or_config):
    class dummy_mapping(object):
        def __init__(self):
            self.D = {"my-organization": (1, "oauth")}
            
        def get_keypair(self, name):
            return self.D[name]
    return dummy_mapping()

class ConfigParseTests(unittest.TestCase):
    INIFILE = u"""\
[base]
organization.name = my-organization

dispatch_function = altaircms.plugins.api:page_type
dispatch_conds = event_page other_page

[event_page]
widgets = 
  image
  freetext

[other_page]
widgets = 
  image
    """

    def _getTarget(self, *args):
        from altaircms.plugins.widget_aggregate import WidgetAggregatorConfig
        return WidgetAggregatorConfig

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def tearDown(self):
        testing.tearDown()

    def setUp(self):
        self.config = testing.setUp()

    def test_dispatch_conds(self):
        configparser = make_config("settings.ini", self.INIFILE)
        target = self._makeOne(self.config, configparser, _organization_mapping=dummy_mapping_utility)
        self.assertEquals(target.dispatch_conds, ["event_page", "other_page"])

    def test_get_organization_name(self):
        configparser = make_config("settings.ini", self.INIFILE)
        target = self._makeOne(self.config, configparser, _organization_mapping=dummy_mapping_utility)
        self.assertEquals(target.organization_name, "my-organization")

    def test_get_keys(self):
        configparser = make_config("settings.ini", self.INIFILE)
        target = self._makeOne(self.config, configparser, _organization_mapping=dummy_mapping_utility)
        self.assertEquals(target.get_keys, (1, "oauth"))

    def test_dispatch_function(self):
        configparser = make_config("settings.ini", self.INIFILE)
        target = self._makeOne(self.config, configparser, _organization_mapping=dummy_mapping_utility)
        from altaircms.plugins.api import page_type
        self.assertEquals(target.dispatch_function, page_type)

    def test_create_subdispatch_dict_with_not_installed_widget(self):
        configparser = make_config("settings.ini", self.INIFILE)
        target = self._makeOne(self.config, configparser, _organization_mapping=dummy_mapping_utility)

        from pyramid.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, lambda : target.create_subdispatch_dict(self.config))

    def test_create_subdispatch_dict_with_installed_widget(self):
        configparser = make_config("settings.ini", self.INIFILE)
        target = self._makeOne(self.config, configparser, _organization_mapping=dummy_mapping_utility)

        self.config.add_directive("add_widgetname", self.config.maybe_dotted("altaircms.plugins.helpers.add_widgetname"))
        self.config.add_widgetname("image")
        self.config.add_widgetname("freetext")

        aggregators = target.create_subdispatch_dict(self.config)
        self.assertEquals(aggregators["event_page"].widgets,  ["image", "freetext"])
        self.assertEquals(aggregators["other_page"].widgets,  ["image"])



class WidgetAggregationDispatcherIntegreationTest(unittest.TestCase):
    inifile = u"""
[base]
organization.name = my-organization

dispatch_function = altaircms.plugins.api:page_type
dispatch_conds = 
   event_page
   other_page

[event_page]
widgets = 
   purchase
   twitter
   rawhtml

[other_page]
widgets = 
   image
   freetext
   rawhtml
"""
    def _callFUT(self, *args, **kwargs):
        from altaircms.plugins.api import parse_inifiles
        return parse_inifiles(*args, **kwargs)
    
    def test_it(self):
        config = testing.setUp()

        ## uglly.....
        from altaircms.auth.api import set_organization_mapping
        set_organization_mapping(config, dummy_mapping_utility(config))

        result = self._callFUT(config, [self.inifile], validator=None, _open=DummyOpen)

        self.assertEquals(result.conts.keys(), [(1, "oauth")])
        self.assertEquals(result.conts[(1, "oauth")]._after_dispatch.keys(), ["event_page", "other_page"])

        ## get widget aggregation dispatcher
        organization = organization=testing.DummyResource(backend_id=1, auth_source="oauth", id=10)
        request = testing.DummyRequest(organization=organization)

        ## event id is none
        aggregator = result.dispatch(request, testing.DummyResource(event_id=None, organization_id=10))
        self.assertEquals(aggregator.widgets, ["image", "freetext", "rawhtml"])

        ## event is is exist
        aggregator = result.dispatch(request, testing.DummyResource(event_id=1, organization_id=10))
        self.assertEquals(aggregator.widgets, ["purchase", "twitter", "rawhtml"])


if __name__ == "__main__":
    ## todo delete it
    # from altaircms.plugins.widget_aggregate import WidgetAggregator
    # wa = WidgetAggregator(["image", "freetext"])

    # request = testing.DummyRequest()
    # print wa.get_widget_paletcode(request)
    # print "--"
    # print wa.get_widget_jscode(request)
    # print "--"
    # # print wa.get_widget_csscode(request)
    unittest.main()

