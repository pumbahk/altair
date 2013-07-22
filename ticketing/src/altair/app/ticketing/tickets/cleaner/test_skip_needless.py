import unittest
from StringIO import StringIO

class SkipNeedLessTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.cleaner.api import skip_needless_content
        return skip_needless_content(*args, **kwargs)

    def test_it(self):
        xml = StringIO("<doc></doc>")
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_prologue(self):
        xml = StringIO('<?xml version="1.0" encoding="UTF-8" ?><doc></doc>')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_prologue_nl(self):
        xml = StringIO('<?xml version="1.0" encoding="UTF-8" ?>\n<doc></doc>')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_comment(self):
        xml = StringIO('<!-- Created with Inkscape (http://www.inkscape.org/) --><doc></doc>')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_comment_nl(self):
        xml = StringIO('<!-- Created with Inkscape (http://www.inkscape.org/) -->\n<doc></doc>')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_comment_nl2(self):
        xml = StringIO('<!-- \n\nCreated with Inkscape \n(http://www.inkscape.org/) -->\n<doc></doc>')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_complex(self):
        xml = StringIO('''<?xml version="1.0" encoding="UTF-8" ?><!-- Created with Inkscape \n(http://www.inkscape.org/) --><doc></doc>''')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_complex2(self):
        xml = StringIO('''<?xml version="1.0" encoding="UTF-8" ?>
<!-- Created with Inkscape \n(http://www.inkscape.org/) --><doc></doc>''')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_complex3(self):
        xml = StringIO('''
<?xml version="1.0" encoding="UTF-8" ?>
<!-- Created with Inkscape \n(http://www.inkscape.org/) -->
<doc></doc>''')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")

    def test_with_complex4(self):
        xml = StringIO('''
<!-- Created with Inkscape \n(http://www.inkscape.org/) -->


<?xml version="1.0" encoding="UTF-8" ?>

<doc></doc>''')
        self._callFUT(xml)
        result = ''.join(x for x in xml)
        self.assertEqual(result, "<doc></doc>")


if __name__ == "__main__":
    unittest.main()
