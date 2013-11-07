# -*- coding:utf-8 -*-
import unittest
import os

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
        self.assertIn(u"""<link rel="stylesheet" href="//foo.bar.jp/css/base.css" type="text/css" media="all">""", result)
        self.assertIn(u"""<link rel="stylesheet" href="//sample-foo/uploaded/:test:/10/css/base.css" type="text/css" media="all">""", result)
        self.assertIn(u"""<link rel="stylesheet" href="//sample-foo/css/top.css" type="text/css" media="all">""", result)

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
        self.assertIn(u"""<img src="//sample-foo/uploaded/:test:/10/img/a.png">""", result)

    def test_background_url(self):
        html = u"""
<style type="text/css">
table.layout {
        background: url(img/bg.jpg)
}
</style>
"""
        result = self._callFUT(self.base_url, html)
        self.assertIn(u"""//sample-foo/uploaded/:test:/10/img/bg.jpg""", result)


    def _callFUT(self, base_url, html_string):
        from io import StringIO
        from lxml import html
        from altaircms.page.staticupload.refine import doc_convert_to_s3link

        doc = html.parse(StringIO(html_string)).getroot()
        doc_convert_to_s3link(doc, base_url)
        return html.tostring(doc)

class UnS3lizeTests(unittest.TestCase):
    base_url = "http://sample-foo/uploaded/:test:/10/"
    def _callFUT(self, base_url, html_string, current_url):
        from io import StringIO
        from lxml import html
        from altaircms.page.staticupload.refine import doc_convert_from_s3link

        doc = html.parse(StringIO(html_string)).getroot()
        doc_convert_from_s3link(doc, base_url, current_url)
        return html.tostring(doc)

    def test_link(self):
        html = u"""
<a href="./index.html"/>
<a href="http://sample-foo/uploaded/:test:/10/howto.html"/>
<a href="http://another.com/link.html"/>
"""
        result = self._callFUT(self.base_url, html, "http://sample-foo/uploaded/:test:/10/howto.html")
        self.assertIn('href="./index.html"', result)
        self.assertIn('href="http://sample-foo/uploaded/:test:/10/howto.html"', result)
        self.assertIn('href="http://another.com/link.html"', result)

    def test_img__top_page(self):
        html = u"""
    <img src="http://sample-foo/uploaded/:test:/10/images/FreshFlower.jpg" width=100 height=100">
"""
        result = self._callFUT(self.base_url, html, "http://sample-foo/uploaded/:test:/10/top.html")
        self.assertIn('src="images/FreshFlower.jpg"', result)

    def test_img__child_page(self):
        html = u"""
    <img src="http://sample-foo/uploaded/:test:/10/images/FreshFlower.jpg" width=100 height=100">
"""
        result = self._callFUT(self.base_url, html, "http://sample-foo/uploaded/:test:/10/child/detail.html")
        self.assertIn('src="../images/FreshFlower.jpg"', result)

    def test_img__grand_child_page(self):
        html = u"""
    <img src="http://sample-foo/uploaded/:test:/10/images/FreshFlower.jpg" width=100 height=100">
"""
        result = self._callFUT(self.base_url, html, "http://sample-foo/uploaded/:test:/10/children/20/detail.html")
        self.assertIn('src="../../images/FreshFlower.jpg"', result)

    def test_another_img__top_page(self):
        html = u"""
    <img src="http://another/images/FreshFlower.jpg" width=100 height=100">
"""
        result = self._callFUT(self.base_url, html, "http://sample-foo/uploaded/:test:/10/top.html")
        self.assertIn('src="http://another/images/FreshFlower.jpg"', result)

    def test_img__top_page__hasnot_protocol(self):
        html = u"""
    <img src="//another/images/FreshFlower.jpg" width=100 height=100">
    <img src="//sample-foo/uploaded/:test:/10/images/FreshFlower.jpg" width=100 height=100">
"""
        result = self._callFUT(self.base_url, html, "http://sample-foo/uploaded/:test:/10/top.html")
        self.assertIn('src="http://another/images/FreshFlower.jpg"', result)
        self.assertIn('src="images/FreshFlower.jpg"', result)


import contextlib
@contextlib.contextmanager
def temporary_file(suffix):
    import tempfile
    _, filename = tempfile.mkstemp(suffix=suffix)
    yield filename
    os.remove(filename)


class UploadIntegrationTests(unittest.TestCase):
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
    def _callFUT(self, *args, **kwargs):
        from altaircms.page.staticupload.refine import refine_link_on_upload
        return refine_link_on_upload(*args, **kwargs)

    def test_it(self):
        with temporary_file(suffix=".html") as tmpname:
            with open(tmpname, "w") as wf:
                wf.write(self.html_string)

            dirname, filename = os.path.split(tmpname)
            result = self._callFUT(filename, dirname, self.Utility)
            self.assertIn(u'href="./link0.html"', result)
            self.assertIn(u'href="link1.html"', result)
            self.assertIn(u'href="foo/../link2.html"', result)
            self.assertIn(u'href="http://www.google.co.jp"', result)

            self.assertIn(u'<img src="//sample-foo/uploaded/:test:/10/images/FreshFlower.jpg"', result)

            self.assertIn(u'href="//sample-foo/uploaded/:test:/10/css/style.css"', result)

    def test_doctype_is_found(self):
        html_string = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
hello!
"""
        with temporary_file(suffix=".html") as tmpname:
            with open(tmpname, "w") as wf:
                wf.write(html_string)

            dirname, filename = os.path.split(tmpname)
            result = self._callFUT(filename, dirname, self.Utility)

            self.assertIn(u'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">', result)



    def test_doctype_is_notfound(self):
        html_string = """hello!"""
        with temporary_file(suffix=".html") as tmpname:
            with open(tmpname, "w") as wf:
                wf.write(html_string)

            dirname, filename = os.path.split(tmpname)
            result = self._callFUT(filename, dirname, self.Utility)
            self.assertNotIn(u'<!DOCTYPE', result)


    def test_not_wrapped_tag(self):
        html_string = """<div>hello!</div>"""
        with temporary_file(suffix=".html") as tmpname:
            with open(tmpname, "w") as wf:
                wf.write(html_string)

            dirname, filename = os.path.split(tmpname)
            result = self._callFUT(filename, dirname, self.Utility)
            self.assertEquals(u'<div>hello!</div>', result)

    def test_not_wrapped_tag2(self):
        html_string = """hello!"""
        with temporary_file(suffix=".html") as tmpname:
            with open(tmpname, "w") as wf:
                wf.write(html_string)

            dirname, filename = os.path.split(tmpname)
            result = self._callFUT(filename, dirname, self.Utility)
            self.assertEquals(u'hello!', result)

    def test_not_wrapped_tag3(self):
        html_string = """<div><style type="text/css"></style><br><br></div>"""
        with temporary_file(suffix=".html") as tmpname:
            with open(tmpname, "w") as wf:
                wf.write(html_string)

            dirname, filename = os.path.split(tmpname)
            result = self._callFUT(filename, dirname, self.Utility)
            self.assertEquals(result.replace("\n", ""), '<div><style type="text/css"></style><br><br></div>')


class DownloadIntegrationTests(unittest.TestCase):
    class Utility:
        @classmethod
        def get_root_url(cls, static_page):
            return "http://sample-foo/uploaded/:test:/10/top.html"

    html_string = u"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
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
    def _callFUT(self, *args, **kwargs):
        from altaircms.page.staticupload.refine import refine_link_on_download_factory
        return refine_link_on_download_factory(*args, **kwargs)

    def test_it(self):
        class StaticPage:
            pass
        with temporary_file(suffix=".html") as tmpname:
            with open(tmpname, "w") as wf:
                wf.write(self.html_string)

            with open(tmpname) as rf:
                result = self._callFUT(StaticPage, self.Utility)(rf, "top.html").read()

            self.assertIn(u'href="./link0.html"', result)
            self.assertIn(u'href="link1.html"', result)
            self.assertIn(u'href="foo/../link2.html"', result)
            self.assertIn(u'href="http://www.google.co.jp"', result)

            self.assertIn(u'<img src="./images/FreshFlower.jpg"', result)

            self.assertIn(u'href="css/style.css"', result)

            self.assertIn(u'<!DOCTYPE', result)

if __name__ == "__main__":
    unittest.main()
