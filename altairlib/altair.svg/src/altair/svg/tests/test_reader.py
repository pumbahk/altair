from unittest import TestCase

class ScannerTest(TestCase):
    def _makeOne(self, *args, **kwargs):
        from ..reader import Scanner
        return Scanner(*args, **kwargs)

    def test_basic(self):
        from lxml import etree
        class Visitor(object):
            _dispatch_map = {
                'a': ('visit_a', ['deco_a'])
                }

            a_decorated = False
            deco_a_called = False
            a_visited = False
            default_visited = False

            def deco_a(self, f):
                self.a_decorated = True
                def wrap(scanner, elem):
                    self.deco_a_called = True
                    f(scanner, elem)    
                return wrap

            def visit_a(self, scanner, elem):
                self.a_visited = True 

            def visit_default(self, scanner, elem):
                self.default_visited = True

        xml = u'''<?xml version="1.0" ?><root><a></a><b></b></root>'''
        xmldoc = etree.ElementTree(etree.fromstring(xml.strip()))

        v = Visitor()
        target = self._makeOne(v)
        self.assertTrue(v.a_decorated)
        target(xmldoc.getroot())
        self.assertTrue(v.deco_a_called)
        self.assertTrue(v.a_visited)
        self.assertTrue(v.default_visited)

    def test_namespace(self):
        from lxml import etree
        class Visitor(object):
            _dispatch_map = {
                '{http://www.example.com/}a': ('visit_a', ['deco_a'])
                }

            a_visited = True

            def visit_a(self, scanner, elem):
                self.a_visited = True 

            def visit_default(self, scanner, elem):
                pass

        xml = u'''<?xml version="1.0" ?><a xmlns="http://www.example.com/"></a>'''
        xmldoc = etree.ElementTree(etree.fromstring(xml.strip()))

        v = Visitor()
        target = self._makeOne(v)
        target([xmldoc.getroot()])
        self.assertTrue(v.a_visited)

