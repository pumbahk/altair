import unittest

class BreadCrumbsOrderTest(unittest.TestCase):
    def _make_page(self, title, parent=None):
        from altaircms.page.models import Page
        return Page.from_dict(dict(title=title, parent=parent))

    def test_single(self):
        page = self._make_page("a")
        self.assertEquals(page.title, "a")
        self.assertEquals([p.title for p in page.ancestors],
                          [])

    def test_it(self):
        page0 = self._make_page("a")
        page1 = self._make_page("b", parent=page0)
        page2 = self._make_page("c", parent=page1)

        self.assertEquals(page2.title, "c")
        self.assertEquals([p.title for p in page2.ancestors], 
                          ["b", "a"])

if __name__ == "__main__":
    unittest.main()

