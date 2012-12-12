import unittest
import json

class PreviewApiViewTests(unittest.TestCase):
    def _getTarget(self):
        from ticketing.tickets.views import PreviewApiView
        return PreviewApiView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_fillvalues_with_product(self):
        class request:
            POST = {"data": json.dumps(dict())}
        target = self._makeOne(None)
        target.preview_fillvalues_with_models()

if __name__ == "__main__":
    unittest.main()

