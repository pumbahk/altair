# -*- encoding:utf-8 -*-

import unittest

"""
絞り込み検索の条件のテスト
"""

def setUpModule():
    import sqlahelper
    from sqlalchemy import create_engine
    import altaircms.page.models
    import altaircms.models

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()

##todo: impement
class SearchByFreewordTests(unittest.TestCase):
    """
1. フリーワードが入力
    全文検索で検索する。copy fieldを使ってsolarで定義してた。取得されるのはpageset.id

    1.a 全てを含む(and結合)
    1.b 少なくとも１つ含む(or結合)

    """
    def _getTarget(self,*args,**kwargs):
        return 
    
    def _makeOne(self, *args, **kwargs):
        return

    def test_it(self):
        pass

class SearchByGanreTests(unittest.TestCase):
    """
2. ジャンルで選択。
    2.a 大ジャンルが選択
      ganre = "music"
      Category.filter(Category.name==genre).filter
    2.b 中ジャンルが選択

    """
    def tearDown(self):
        import transaction
        transaction.abort()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()

    def _callFUT(self, *args,**kwargs):
        from altairsite.search.searcher import  search_by_ganre
        return search_by_ganre(*args, **kwargs)

    def _category(self, *args, **kwargs):
        from altaircms.models import Category
        o = Category(*args, **kwargs)
        self.session.add(o)
        return o

    def _pageset(self, *args, **kwargs):
        from altaircms.page.models import PageSet
        o = PageSet(*args, **kwargs)
        self.session.add(o)
        return o

    def test_no_refine(self):
        qs = object()
        result = self._callFUT([], [], qs=qs)
        self.assertEquals(qs, result)

    def test_found_with_top_categories(self):
        music = self._category(name="music", hierarchy=u"top-hierarchy")
        jpop_top_page = self._pageset()
        jpop = self._category(name="jpop", parent=music, pageset=jpop_top_page, hierarchy=u"middle-hierarchy")
        detail_page = self._pageset(parent=jpop_top_page)

        self.session.flush()
        result = self._callFUT(["music"], [])

        self.assertEquals(1, result.count())
        self.assertEquals(detail_page, result[0])

    def test_not_found_with_top_categories(self):
        music = self._category(name="music", hierarchy=u"top-hierary")
        other_category = self._category(name="other-ganre-category", hierarchy=u"top-hierarchy")

        jpop_top_page = self._pageset()
        jpop = self._category(name="jpop", parent=other_category, pageset=jpop_top_page, hierarchy=u"middle-hierarchy")
        detail_page = self._pageset(parent=jpop_top_page)

        self.session.flush()
        result = self._callFUT(["music"], [])

        self.assertEquals([], list(result))

    def test_found_with_sub_categories(self):
        jpop_top_page = self._pageset()
        jpop = self._category(name="jpop", pageset=jpop_top_page, hierarchy=u"middle-hierarchy")
        detail_page = self._pageset(parent=jpop_top_page)

        self.session.flush()
        result = self._callFUT([], ["jpop"])

        self.assertEquals(1, result.count())
        self.assertEquals(detail_page, result[0])

    def test_not_found_with_sub_categories(self):
        jpop_top_page = self._pageset()
        jpop = self._category(name="jpop", pageset=jpop_top_page, hierarchy=u"middle-hierarchy")
        other_page = self._pageset()
        detail_page = self._pageset(parent=other_page)

        self.session.flush()
        result = self._callFUT([], ["jpop"])

        self.assertEquals([], list(result))


class SearchByAreaTests(unittest.TestCase):
    """
3. エリアで選択
    3.a 地域区分が選択
    3.b 県名が選択

    """

    def tearDown(self):
        import transaction
        transaction.abort()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()

    def _callFUT(self, *args, **kwargs):
        from altairsite.search.searcher import  search_by_area
        return search_by_area(*args, **kwargs)

    def test_no_refine(self):
        qs = object()
        result = self._callFUT([], qs=qs)
        self.assertEquals(qs, result)

    def test_match_with_prefectures(self):
        from altaircms.models import Performance
        from altaircms.event.models import Event
        from altaircms.page.models import PageSet
        event = Event()
        p0 = Performance(venue=u"hokkaido", event=event, backend_performance_id=1111)
        p1 = Performance(venue=u"hokkaido", event=event, backend_performance_id=1112)
        page = PageSet(event=event)

        self.session.add_all([page, event, p0, p1])
        self.session.flush()
        
        result = self._callFUT([u"hokkaido"])

        self.assertEquals([page], list(result))

    def test_unmatch_with_prefectures(self):
        from altaircms.models import Performance
        from altaircms.event.models import Event
        from altaircms.page.models import PageSet
        event = Event()
        p0 = Performance(venue=u"tokyo", event=event, backend_performance_id=1111)
        p1 = Performance(venue=u"tokyo", event=event, backend_performance_id=1112)
        p2 = Performance(venue=u"hokkaido", backend_performance_id=1113) #orphan
        page = PageSet(event=event)

        self.session.add_all([page, event, p0, p1, p2])
        self.session.flush()

        result = self._callFUT([u"hokkaido"])

        self.assertEquals([], list(result))

class SearchByDealCondFlagsTests(unittest.TestCase):
    """
5. 販売条件の中のフラグがチェックされている
    """

    def _getTarget(self,*args,**kwargs):
        return 

    def _makeOne(self, *args, **kwargs):
        return

    def test_it(self):
        pass


class SearchByAddedServiceFlagsTests(unittest.TestCase):
    """
6. 付加サービスの中のフラグがチェックされている
"""
   
    def _getTarget(self,*args,**kwargs):
        return 

    def _makeOne(self, *args, **kwargs):
        return

    def test_it(self):
        pass


class SearchByAboutDealPartTests(unittest.TestCase):
    """
7. 発売日
    7.a N日以内に発送の欄が入力される
    7.b 販売終了までN日
    7.c 販売終了を検索に含める
    7.d 公演中止を検索に含める
    """

    def _getTarget(self,*args,**kwargs):
        return 

    def _makeOne(self, *args, **kwargs):
        return

    def test_it(self):
        pass


if __name__ == "__main__":
    unittest.main()
