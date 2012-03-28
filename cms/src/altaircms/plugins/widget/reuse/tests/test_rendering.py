# -*- coding:utf-8 -*-

from contextlib import contextmanager
from altaircms.models import DBSession
from pyramid.testing import DummyRequest

import unittest
import mock
from altaircms.plugins.widget.reuse.models import ReuseWidget
from pyramid.testing import setUp
from pyramid.testing import tearDown
from altaircms.page.models import Page
from altaircms.page.models import Layout

import os 
here = os.path.abspath(os.path.dirname(__file__))
class RenderingTest(unittest.TestCase):
    def tearDown(self):
        tearDown()

    def _getBsettings(self, **kwargs):
        class BSettings(dict):
            def need_extra_in_scan(self, k):
                return k in self.extra
            def scan(self):
                for k, v in self.items():
                    self[k] = v() if callable(v) else v
            add = dict.__setitem__
        ins = BSettings()
        for k, v in kwargs.items():
            setattr(ins, k, v)
        return ins

    def _getAppConfig(self, request=None):
        config = setUp(request=request)
        config.registry.settings["mako.directories"] = here
        config.registry.settings["altaircms.layout_directory"] = "altaircms:plugins/widget/reuse/tests"
        config.registry.settings["mako.input_encoding"] = "utf-8"
        config.registry.settings["altaircms.plugin_static_directory"] = here
        config.include("altaircms.front", route_prefix="f")
        config.include("altaircms.plugins.widget.reuse") #attach event
        config.scan("altaircms.subscribers") #attach event
        return config

    def _getRequest(self):
        request = DummyRequest()
        request.user = None
        return request

    def _getTarget(self, **kwargs):
        w = ReuseWidget(source_page=Page(layout=Layout(template_filename="layout.mako")))
        for k, v in kwargs.items():
            setattr(w, k, v)
        return w

    @mock.patch("altaircms.plugins.widget.reuse.models.ReuseWidget._get_internal_content", return_value="<div>subpage</div>")
    def test_render_outer(self, mocked):
        """renderable if a inner content rendered completety"""
        request = self._getRequest()
        self._getAppConfig(request)

        widget = self._getTarget(attrs="{}")
        bsettings = self._getBsettings(extra={"request": request})
        widget.merge_settings("subarea", bsettings)
        bsettings.scan()
        self.assertEquals(bsettings["subarea"], """\
<div >
   <div>subpage</div>
</div>
""")

    def test_render_full(self):
        """renderable """
        request = self._getRequest()
        self._getAppConfig(request)

        widget = self._getTarget(attrs='{"class": "promotion", "id": "followme"}')
        bsettings = self._getBsettings(extra={"request": request})
        widget.merge_settings("subarea", bsettings)
        bsettings.scan()
        self.assertEquals(bsettings["subarea"].replace("\n", ""), 
                          u'<div class="promotion" id="followme">   にほんご woo,whee!</div>')

    def test_css_setting_with_width(self):
        """ css settings is generated if widget's width is boound value' """
        request = self._getRequest()
        self._getAppConfig(request)

        widget = self._getTarget(attrs='{"class": "promotion", "id": "followme"}',
                                 width=100)
        bsettings = self._getBsettings(extra={"request": request})
        widget.merge_settings("subarea", bsettings)
        bsettings.scan()
        self.assertTrue(".width {promotion: 100;}" in bsettings["css_prerender"])


if __name__ == "__main__":
    unittest.main()
