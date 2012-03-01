import json
import unittest

class WidgetCacherTest(unittest.TestCase):
    def _getTarget(self, fetcher=None):
        from altaircms.widget.generate import WidgetCacher        
        return WidgetCacher(fetcher)

    def _getPage(self):
        class page(object):
            structure = json.dumps(
                {"header": [{"name": "dummy_widget",  "pk": 1}], 
                 "footer": [{"name": "dummy_widget",  "pk": 2}], 
                 })
        return page

    def test_is_scanned_false_before_scan(self):
        cacher = self._getTarget()
        page = self._getPage()

        self.assertFalse(cacher.is_scanned(page))

    def test_is_scanned_true_after_scan(self):
        cacher = self._getTarget()
        page = self._getPage()

        cacher.scan(page)
        self.assertTrue(cacher.is_scanned(page))

    def test_is_scanned_false_another_page(self):
        cacher = self._getTarget()
        page = self._getPage()
        cacher.scan(page)

        another = self._getPage()
        self.assertTrue(cacher.is_scanned(page))
        self.assertFalse(cacher.is_scanned(another))

    def getFetcher(self):
        class Objectlike(dict):
            __getattr__ = dict.__getitem__
        D = {
            "dummy_widget": [
                Objectlike(id=1, asset_id=10), 
                Objectlike(id=2, asset_id=20), 
                Objectlike(id=3, asset_id=30), 
                ], 
            "text_widget": [
                Objectlike(id=4, text=u"foo"), 
                Objectlike(id=5, text=u"bar"),
                ]
            }
        class Fetcher(object):
            def fetch(self, name, pks):
                return D.get(name)
        return Fetcher()

    def test_fetch(self):
        fetcher = self.getFetcher()
        cacher = self._getTarget(fetcher)
        page = self._getPage()

        cacher.scan(page)
        cacher.fetch()

        self.assertEquals(cacher.result["dummy_widget"][1].asset_id, 10)
        self.assertEquals(cacher.result["dummy_widget"][2].asset_id, 20)
    
    def test_fetch_not_found_key(self):
        fetcher = self.getFetcher()
        cacher = self._getTarget(fetcher)
        page = self._getPage()

        cacher.scan(page)
        cacher.fetch()

        self.assertEquals(cacher.result["dummy_widget"][1].asset_id, 10)
        self.assertRaises(lambda : cacher.result["dummy_widget"][5].asset_id)

    def test_to_widget_tree_has_block(self):
        fetcher = self.getFetcher()
        cacher = self._getTarget(fetcher)
        page = self._getPage()

        cacher.scan(page)
        cacher.fetch()
        self.assertTrue(cacher.to_widget_tree(page).blocks)

    def test_to_widget_tree_short_cut(self):
        fetcher = self.getFetcher()
        cacher = self._getTarget(fetcher)
        page = self._getPage()

        self.assertTrue(cacher.to_widget_tree(page).blocks)
        cacher.to_widget_tree(page)

    def test_to_widget_blocks_has_block(self):
        fetcher = self.getFetcher()
        cacher = self._getTarget(fetcher)
        page = self._getPage()

        cacher.scan(page)
        cacher.fetch()
        blocks = cacher.to_widget_tree(page).blocks
        self.assertTrue("header" in blocks)
        self.assertTrue("footer" in blocks)

    def test_to_widget_blocks_has_collect_member(self):
        fetcher = self.getFetcher()
        cacher = self._getTarget(fetcher)
        page = self._getPage()

        cacher.scan(page)
        cacher.fetch()
        blocks = cacher.to_widget_tree(page).blocks

        self.assertEquals([o.asset_id for o in blocks["header"]], [10])
        self.assertEquals([o.asset_id for o in blocks["footer"]], [20])

if __name__ == "__main__":
    unittest.main()
