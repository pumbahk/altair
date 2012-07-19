import unittest
from pyramid import testing

class FrontRenderingTests(unittest.TestCase):
    def _getTarget(self, *args):
        from altaircms.front.resources import AccessControl
        return AccessControl

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_it(self):
        testing.DummyRequest()
        pass

if __name__ == "__main__":
    unittest.testmain()

