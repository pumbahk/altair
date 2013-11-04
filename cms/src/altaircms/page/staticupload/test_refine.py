# -*- coding:utf-8 -*-
import unittest

class LinkRewriteTests(unittest.TestCase):
    base_url = "http://sample-foo/uploaded/:test:/10/"

    def test_has_not_protocol(self):
        html = u"""
<link rel="stylesheet" href="//foo.bar.jp/css/base.css" type="text/css" media="all">
"""
        result = self._callFUT(self.base_url, html)
        self.assertIn(u"""<link rel="stylesheet" href="//foo.bar.jp/css/base.css" type="text/css" media="all">""", result)


    def test_css(self):
        html = u"""
<link rel="stylesheet" href="http://foo.bar.jp/css/base.css" type="text/css" media="all">
<link rel="stylesheet" href="css/base.css" type="text/css" media="all">
<link rel="stylesheet" href="/css/top.css" type="text/css" media="all">
"""
        result = self._callFUT(self.base_url, html)
        self.assertIn(u"""<link rel="stylesheet" href="http://foo.bar.jp/css/base.css" type="text/css" media="all">""", result)
        self.assertIn(u"""<link rel="stylesheet" href="http://sample-foo/uploaded/:test:/10/css/base.css" type="text/css" media="all">""", result)
        self.assertIn(u"""<link rel="stylesheet" href="http://sample-foo/css/top.css" type="text/css" media="all">""", result)

    def test_link(self):
        html = u"""
<a href="link.html">link</a>
"""
        result = self._callFUT(self.base_url, html)
        self.assertIn(u"""<a href="link.html">link</a>""", result)

    def test_js(self):
        html = u"""
<script src="js/app.js" type="text/javascript"/>
"""
        result = self._callFUT(self.base_url, html)
        self.assertIn(u"""<script src="js/app.js" type="text/javascript">""", result)

    def test_img(self):
        html = u"""
<img src="img/a.png"/>
"""
        result = self._callFUT(self.base_url, html)
        self.assertIn(u"""<img src="http://sample-foo/uploaded/:test:/10/img/a.png">""", result)

    def test_background_url(self):
        html = u"""
<style type="text/css">
table.layout {
        background: url(img/bg.jpg)
}
</style>
"""
        result = self._callFUT(self.base_url, html)
        self.assertIn(u"""http://sample-foo/uploaded/:test:/10/img/bg.jpg""", result)


    def _callFUT(self, base_url, html_string):
        from io import StringIO
        from lxml import html
        from altaircms.page.staticupload.refine import _make_links_absolute

        doc = html.parse(StringIO(html_string)).getroot()
        _make_links_absolute(doc, self.base_url)
        return html.tostring(doc)

import contextlib
@contextlib.contextmanager
def temporary_file():
    import os
    import tempfile
    _, filename = tempfile.mkstemp()
    yield filename
    os.remove(filename)

class IntegrationTests(unittest.TestCase):
    class Utility:
        @classmethod
        def get_base_url(cls, dirname, fname):
            return "http://sample-foo/uploaded/:test:/10/"

    html_string = u"""
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" type="text/css" href="css/style.css">
  </head>
  <body>
    <img src="./images/FreshFlower.jpg" width=100 height=100>
    <a href="./link0.html">link0</a>
    <a href="link1.html">link1</a>
    <a href="foo/../link2.html">link2</a>
    <a href="http://www.google.co.jp">google</a>
  </body>
</html>
"""

    def test_it(self):
        import os
        with temporary_file() as filename:
            with open(filename, "w") as wf:
                wf.write(self.html_string)

            dirname, filename = os.path.split(filename)
            from altaircms.page.staticupload.refine import refine_link_as_string
            result = refine_link_as_string(filename, dirname, self.Utility)

            self.assertIn(u'href="./link0.html"', result)
            self.assertIn(u'href="link1.html"', result)
            self.assertIn(u'href="foo/../link2.html"', result)
            self.assertIn(u'href="http://www.google.co.jp"', result)

            self.assertIn(u'href="http://sample-foo/uploaded/:test:/10/css/style.css"', result)

if __name__ == "__main__":
    unittest.main()
