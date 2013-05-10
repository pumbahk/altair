import unittest
from pyramid import testing

class DummyFileSession(object):
    options = "OPTION"
    def __init__(self):
        self.result = []
    def add(self, x):
        self.result.append(("add", x))
    def delete(self, x):
        self.result.append(("delete", x))
    def commit(self, extra_args=None):
        return self.result

class HasRequestSessionTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, *args, **kwargs):
        from altaircms.filelib.adapts import AdaptsFileSession
        class request:
            registry = self.config.registry
        return AdaptsFileSession(request, DummyFileSession())
        
    def test_it(self):
        from altaircms.filelib.adapts import AfterCommit
        def asseration(event):
            self.assertEquals(event.result, [("add", "a"), ("delete", "b")])
            self.assertEquals(event.options, "OPTION")
        self.config.add_subscriber(asseration, AfterCommit)

        target = self._makeOne()
        target.add("a")
        target.delete("b")
        target.commit()
        

if __name__ == "__main__":
    unittest.main()
