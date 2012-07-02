# -*- encoding:utf-8 -*-
import unittest

def setUpModule():
    import altaircms.page.models
    import altaircms.page.models
    import altaircms.models
    from sqlalchemy import create_engine
    import sqlahelper

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()


class FindSubCategoryFromPageTests(unittest.TestCase):
    def _callFUT(self, page, *args, **kwargs):
        from altairsite.front.helpers import get_subcategories_from_page
        return get_subcategories_from_page(page, *args, **kwargs)

    def tearDown(self):
        from altaircms.models import DBSession
        DBSession.remove()

    def _make_page(self):
        from altaircms.page.models import Page
        from altaircms.page.models import PageSet
        from altaircms.models import DBSession

        pageset = PageSet()
        page = Page(pageset=pageset)
        DBSession.add(page)
        return page

    def _make_category(self, name, parent=None, pageset=None, **kwargs):
        from altaircms.models import DBSession
        from altaircms.models import Category

        category = Category(name=name, parent=parent, pageset=pageset, **kwargs)
        DBSession.add(category)
        return category

    def test_from_category_top_page(self):
        target_page = self._make_page()

        category_top = self._make_category(name="top", pageset=target_page.pageset, 
                                           hierarchy=u"top-category")
        suba = self._make_category(name="subA", parent=category_top, 
                                   hierarchy=u"sub-category")
        subb = self._make_category(name="subB", parent=category_top, 
                                   hierarchy=u"sub-category")
        
        request = None
        result = self._callFUT(request, target_page)

        self.assertEquals(sorted([suba, subb]), sorted(result))

    def test_from_category_detail_page(self):
        ## detail page hasn't sub categories
        target_page = self._make_page()
        
        request = None
        result = self._callFUT(request, target_page)
        
        self.assertEquals([], result)

if __name__ == "__main__":
    unittest.main()
