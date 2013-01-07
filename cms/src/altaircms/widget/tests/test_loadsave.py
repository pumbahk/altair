import unittest
import json

class WidgetStructureSaveTest(unittest.TestCase):
    def _getTarget(self):
        from altaircms.widget.models import WidgetDisposition
        return WidgetDisposition

    def _makeOne(self, *args, **kwargs):
        return self._getTarget(*args, **kwargs)

    def test_shallow_copy(self):
        target = self._makeOne()

        class page:
            title = "this-is-page"
            organization_id = 1
            class layout:
                blocks = json.dumps([["x"], ["y"], ["z"]])
            structure = json.dumps({
                u'x': [{u'pk': None, u'name': u'freetext'}, {u'pk': None, u'name': u'twitter'}, {u'pk': None, u'name': u'purchase'}], 
                u'y': [{u'pk': None, u'name': u'topic'}],
                u'z': [{u'pk': None, u'name': u'image'}, {u'pk': None, u'name': u'heading'}]
            })

        result = target.shallow_copy_from_page(page, None)
        self.assertEquals(result.structure, 
                          json.dumps({"x": [{"name": "freetext"}, {"name": "twitter"}, {"name": "purchase"}], 
                                      "y": [{"name": "topic"}], 
                                      "z": [{"name": "image"}, {"name": "heading"}]}))


if __name__ == "__main__":
    import altaircms.page.models
    import altaircms.event.models
    import altaircms.auth.models
    import altaircms.models
    unittest.main()
