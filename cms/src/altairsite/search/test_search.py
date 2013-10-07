# -*- encoding:utf-8 -*-

import unittest
from datetime import datetime
from datetime import timedelta
from altaircms.testing import setup_db, teardown_db
"""
絞り込み検索の条件のテスト
"""

def setUpModule():
    setup_db(
        ["altaircms.page.models", 
         "altaircms.event.models", 
         "altaircms.models", 
         "altaircms.tag.models", 
         "altaircms.widget.models", 
         "altaircms.asset.models"]
        )

def tearDownModule():
    teardown_db()

def _tag_labels_from_genres(genres):
    S = set()
    for g in genres:
        S.add(g.label)
        for c in g.ancestors:
            S.add(c.label)
    return list(S)

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

class SearchByGenreTests(unittest.TestCase):
    """
    2. ジャンルで選択。
    2.a 大ジャンルが選択
      genre = "music"
    2.b 中ジャンルが選択

    """
    def tearDown(self):
        import transaction
        transaction.abort()
        from altaircms.models import DBSession
        DBSession.remove()
        from pyramid.testing import tearDown
        tearDown()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()

        from pyramid.testing import setUp
        self.config = setUp()
        class organization:
            id = 1
        self.config.organization = organization
        self.config.include("altaircms.page.install_pageset_searcher")

    def _callFUT(self, *args,**kwargs):
        from altairsite.search.searcher import  search_by_genre
        return search_by_genre(*args, **kwargs)

    def _genre(self, **kwargs):
        from altaircms.models import Genre
        o = Genre(organization_id=self.config.organization.id, **kwargs)
        self.session.add(o)
        return o

    def _pageset(self, *args, **kwargs):
        from altaircms.page.models import PageSet
        o = PageSet(*args, **kwargs)
        self.session.add(o)
        return o

    def test_no_refine(self):
        qs = object()
        result = self._callFUT(None, qs, [], [])
        self.assertEquals(qs, result)

    def test_found_with_top_categories(self):
        from altaircms.page.models import PageSet, PageTag
        top = self._genre(name=u"top")
        music = self._genre(label=u"音楽")
        jpop = self._genre(label=u"jポップ")
        sports = self._genre(label=u"スポーツ")

        jpop.add_parent(music)
        jpop.add_parent(top, hop=2)
        music.add_parent(top)
        sports.add_parent(top)
        detail_page = self._pageset(genre=jpop)
        from altaircms.tag.api import put_system_tags
        put_system_tags(detail_page, "page", _tag_labels_from_genres([jpop]), self.config)
        self.session.flush()

        system_tag = PageTag.query.filter_by(organization_id=None, label=u"音楽").first()
        result = self._callFUT(self.config, PageSet.query, [system_tag.id])
        self.assertEquals(1, result.count())
        self.assertEquals(detail_page, result[0])

    def test_not_found_with_top_categories(self):
        from altaircms.page.models import PageSet
        top = self._genre(name=u"top")
        music = self._genre(label=u"音楽")
        jpop = self._genre(label=u"jポップ")
        sports = self._genre(label=u"スポーツ")

        jpop.add_parent(music)
        jpop.add_parent(top, hop=2)
        music.add_parent(top)
        sports.add_parent(top)
        detail_page = self._pageset(genre=jpop)
        from altaircms.tag.api import put_system_tags
        put_system_tags(detail_page, "page", _tag_labels_from_genres([jpop]), self.config)
        self.session.flush()
        result = self._callFUT(self.config, PageSet.query, [10000])
        self.assertEquals([], list(result))

    def test_found_with_sub_categories(self):
        from altaircms.page.models import PageSet, PageTag
        top = self._genre(name=u"top")
        music = self._genre(label=u"音楽")
        jpop = self._genre(label=u"jポップ")

        jpop.add_parent(music)
        jpop.add_parent(top, hop=2)
        music.add_parent(top)
        detail_page = self._pageset(genre=jpop)
        from altaircms.tag.api import put_system_tags
        put_system_tags(detail_page, "page", _tag_labels_from_genres([jpop]), self.config)
        self.session.flush()

        system_tag = PageTag.query.filter_by(organization_id=None, label=u"jポップ").first()
        result = self._callFUT(self.config, PageSet.query, [system_tag.id])
        self.assertEquals(1, result.count())
        self.assertEquals(detail_page, result[0])

    def test_not_found_with_sub_categories(self):
        from altaircms.page.models import PageSet
        top = self._genre(name=u"top")
        music = self._genre(label=u"音楽")
        jpop = self._genre(label=u"jポップ")
        anime = self._genre(label=u"anime")

        jpop.add_parent(music)
        jpop.add_parent(top, hop=2)
        anime.add_parent(music)
        anime.add_parent(top, hop=2)
        music.add_parent(top)
        detail_page = self._pageset(genre=jpop)
        from altaircms.tag.api import put_system_tags
        put_system_tags(detail_page, "page", _tag_labels_from_genres([jpop]), self.config)
        self.session.flush()

        result = self._callFUT(self.config, PageSet.query, [10000])
        self.assertEquals([], list(result))

class EventsByAreaTests(unittest.TestCase):
    """
3. エリアで選択
    3.a 地域区分が選択
    3.b 県名が選択

    """

    def tearDown(self):
        import transaction
        transaction.abort()
        from altaircms.models import DBSession
        DBSession.remove()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()

    def _callFUT(self, *args, **kwargs):
        from altairsite.search.searcher import  events_by_area
        return events_by_area(*args, **kwargs)

    def test_no_refine(self):
        qs = object()
        result = self._callFUT(qs, [])
        self.assertEquals(qs, result)

    def test_match_with_prefectures(self):
        from altaircms.models import Performance
        from altaircms.event.models import Event
        event = Event()
        p0 = Performance(prefecture=u"hokkaido", event=event, backend_id=1111)
        p1 = Performance(prefecture=u"hokkaido", event=event, backend_id=1112)

        self.session.add_all([event, p0, p1])
        self.session.flush()
        
        result = self._callFUT(Event.query, [u"hokkaido"])

        self.assertEquals([event], list(result))

    def test_unmatch_with_prefectures(self):
        from altaircms.models import Performance
        from altaircms.event.models import Event
        event = Event()

        p0 = Performance(prefecture=u"tokyo", event=event, backend_id=1111)
        p1 = Performance(prefecture=u"tokyo", event=event, backend_id=1112)
        p2 = Performance(prefecture=u"hokkaido", backend_id=1113) #orphan

        self.session.add_all([event, p0, p1, p2])
        self.session.flush()

        result = self._callFUT(Event.query, [u"hokkaido"])

        self.assertEquals([], list(result))


class EventsByPerformanceTermTests(unittest.TestCase):
    """
4. 公演日で探す
    4.a 開始日が設定されている場合
    4.b 終了日が設定されている場合
    4.c 両方が設定されている場合
    """
    def tearDown(self):
        import transaction
        transaction.abort()
        from altaircms.models import DBSession
        DBSession.remove()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()


    def _callFUT(self, *args, **kwargs):
        from altairsite.search.searcher import events_by_performance_term
        return events_by_performance_term(*args, **kwargs)

    @unittest.skip ("* #5609: must fix")
    def test_search_by_start_on(self):
        from altaircms.event.models import Event

        ev0 = Event(event_open=datetime(2011, 1, 1))
        ev1 = Event(event_open=datetime(2012, 1, 1))

        self.session.add_all([ev0, ev1])

        result = self._callFUT(Event.query, datetime(2011, 9, 9), None)

        self.assertEquals(1, result.count())
        self.assertEquals([ev1], list(result))

    def test_search_by_end_on(self):
        from altaircms.event.models import Event

        ev0 = Event(event_close=datetime(2011, 1, 1))
        ev1 = Event(event_close=datetime(2012, 1, 1))

        self.session.add_all([ev0, ev1])

        result = self._callFUT(Event.query, None, datetime(2011, 9, 9))

        self.assertEquals(1, result.count())
        self.assertEquals([ev0], list(result))

    def test_search_by_both_on(self):
        from altaircms.event.models import Event

        ev0 = Event(event_open=datetime(2011, 1, 1), event_close=datetime(2011, 2, 1))
        ev1 = Event(event_open=datetime(2012, 1, 1), event_close=datetime(2011, 4, 1))

        self.session.add_all([ev0, ev1])

        result = self._callFUT(Event.query, datetime(2011, 1, 1), datetime(2011, 3, 1))

        self.assertEquals(1, result.count())
        self.assertEquals([ev0], list(result))


        result = self._callFUT(Event.query, datetime(2011, 1, 1), datetime(2011, 4, 1))

        self.assertEquals(2, result.count())
        self.assertEquals([ev0, ev1], list(result))

class EventsByDealCondFlagsTests(unittest.TestCase):
    """
5. 販売条件の中のフラグがチェックされている
todo: 作成
    """

    def _callFUT(self,*args,**kwargs):
        from altairsite.search.searcher import events_by_deal_cond_flags
        return events_by_deal_cond_flags(*args, **kwargs)

    def tearDown(self):
        import transaction
        transaction.abort()
        from altaircms.models import DBSession
        DBSession.remove()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()

    @unittest.skip ("* #5609: must fix")
    def test_nodata_not_found(self):
        from altaircms.event.models import Event
        qs = Event.query
        
        result = self._callFUT(qs, [u"1"])
        self.assertEquals([], list(result))

    @unittest.skip ("* #5609: must fix")
    def test_unmatched_param__notfound(self):
        from altaircms.event.models import Event
        from altaircms.models import SalesSegmentGroup
        qs = Event.query

        event = Event()
        sale = SalesSegmentGroup(event=event, kind_id=1)
        self.session.add(sale)

        result = self._callFUT(qs, [u"2"])
        self.assertEquals([], list(result))

    @unittest.skip ("* #5609: must fix")
    def test_matched_param__found(self):
        from altaircms.event.models import Event
        from altaircms.models import SalesSegmentGroup
        qs = Event.query

        event = Event()
        sale = SalesSegmentGroup(event=event, kind_id=1)
        self.session.add(sale)

        result = self._callFUT(qs, [u"1"])
        self.assertEquals([event], list(result))

    @unittest.skip ("* #5609: must fix")
    def test_search_unionly(self):
        from altaircms.event.models import Event
        from altaircms.models import SalesSegmentGroup
        qs = Event.query

        event = Event()
        sale = SalesSegmentGroup(event=event, kind_id=u"1")
        self.session.add(sale)

        result = self._callFUT(qs, [u"0", u"2", u"3"])
        self.assertEquals([], list(result))

        result = self._callFUT(qs, [u"0", u"1", u"2", u"3"])
        self.assertEquals([event], list(result))

    ## todo: saleのtodo:公開開始。終了見る
        #これは別の場所で見ているのでok

class EventsByAddedServiceFlagsTests(unittest.TestCase):
    """
6. 付加サービスの中のフラグがチェックされている
todo: 作成
"""
   
    def _getTarget(self,*args,**kwargs):
        return 

    def _makeOne(self, *args, **kwargs):
        return

    def test_it(self):
        pass

class EventsByAboutDealPartTests(unittest.TestCase):
    """
7. 発売日
    7.a N日以内に発送の欄が入力される
    7.b 販売終了までN日
    7.c 販売終了を検索に含める
    7.d 公演中止を検索に含める
    """
    def tearDown(self):
        import transaction
        transaction.abort()
        from altaircms.models import DBSession
        DBSession.remove()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()

    def _callFUT(self, *args, **kwargs):
        from altairsite.search.searcher import events_by_about_deal
        return events_by_about_deal(*args, **kwargs)

    @unittest.skip ("* #5609: must fix")
    def test_by_deal_open_(self):
        from altaircms.event.models import Event
        
        ev0 = Event(deal_open=datetime(2012, 1, 1)+timedelta(days=-10))
        ev1 = Event(deal_open=datetime(2012, 1, 1)+timedelta(days=0))
        ev2 = Event(deal_open=datetime(2012, 1, 1)+timedelta(days=10))
        ev3 = Event(deal_open=datetime(2012, 1, 1)+timedelta(days=20))

        self.session.add_all([ev0, ev1, ev2, ev3])

        result = self._callFUT(Event.query, 15, None, None, None, _nowday=lambda : datetime(2012, 1, 1))

        self.assertEquals(2, result.count())
        self.assertEquals([ev1, ev2], list(result))

    @unittest.skip ("* #5609: must fix")
    def test_by_deal_end(self):
        from altaircms.event.models import Event
        
        ev0 = Event(deal_close=datetime(2012, 1, 1)+timedelta(days=-10))
        ev1 = Event(deal_close=datetime(2012, 1, 1)+timedelta(days=0))
        ev2 = Event(deal_close=datetime(2012, 1, 1)+timedelta(days=10))
        ev3 = Event(deal_close=datetime(2012, 1, 1)+timedelta(days=20))

        self.session.add_all([ev0, ev1, ev2, ev3])

        result = self._callFUT(Event.query, None, 15, None, None, _nowday=lambda : datetime(2012, 1, 1))

        self.assertEquals(2, result.count())
        self.assertEquals([ev1, ev2], list(result))

    @unittest.skip ("* #5609: must fix")
    def test_by_closed_only(self):
        from altaircms.event.models import Event
        
        ev0 = Event(deal_close=datetime(2012, 1, 1)+timedelta(days=-10))
        ev1 = Event(deal_close=datetime(2012, 1, 1)+timedelta(days=0))
        ev2 = Event(deal_close=datetime(2012, 1, 1)+timedelta(days=10))

        self.session.add_all([ev0, ev1, ev2])

        ### チェック入れない場合には終了したものが検索対象に含まれない
        result = self._callFUT(Event.query, None, None, None, None, _nowday=lambda : datetime(2012, 1, 1))
        self.assertEquals(2, result.count())
        self.assertEquals([ev1, ev2], list(result))

        ### チェック入れた場合には終了したものみが検索対象に含まれる
        result = self._callFUT(Event.query, None, None, True, None, _nowday=lambda : datetime(2012, 1, 1))
        self.assertEquals(1, result.count())
        self.assertEquals([ev0], list(result))

    @unittest.skip ("* #5609: must fix")
    def test_by_canceld_only(self):
          from altaircms.event.models import Event
          from altaircms.models import Performance
  
          ev0 = Event()
          pef00 = Performance(event=ev0, open_on=datetime(2012, 1, 1), backend_id=0)
          pef01 = Performance(event=ev0, open_on=datetime(2012, 1, 4), backend_id=1, canceld=True)
          ev1 = Event()
          pef10 = Performance(event=ev1, open_on=datetime(2012, 1, 1), backend_id=2)
          pef11 = Performance(event=ev1, open_on=datetime(2012, 1, 4), backend_id=3)
  
          self.session.add_all([ev0, ev1, pef00, pef01, pef10, pef11])

          ## 通常は、キャンセルしたものなど関係なく見える
          result = self._callFUT(Event.query, None, None, None, False, _nowday=lambda : datetime(2012, 1, 1))
          self.assertEquals([ev0, ev1], list(result))
  
          ## canceld onlyのcheckboxをチェックするとキャンセルが発生したイベントのみを検索対象にする
          ## キャンセルが発生したイベント = イベント中の公演(performance)の中にキャンセル（公演中止）が発生したイベントのこと
          result = self._callFUT(Event.query, None, None, None, True, _nowday=lambda : datetime(2012, 1, 1))
          self.assertEquals([ev0], list(result))



class SearchOnlyIsSearcheableEventTests(unittest.TestCase):
    """ 検索可能なもののみが取れるようになっているか調べる
    """

    def test_it(self):
        from altairsite.search.searcher import get_pageset_query_fullset
        from altaircms.testing import DummyRequest
        result =  str(get_pageset_query_fullset(DummyRequest(), {}))
        
        self.assertIn("event.is_searchable = ? AND event.id = pagesets.event_id", result)



class SearchOrderTests(unittest.TestCase):
    """
    販売終了間近なものから順に表示される
    """
    def _callFUT(self, qs, *args, **kwargs):
        from altairsite.search.searcher import _refine_pageset_search_order
        return _refine_pageset_search_order(qs)

    def tearDown(self):
        from altaircms.models import DBSession
        DBSession.remove()

    def _make_pageset(self, id=None, deal_close=None):
        from altaircms.event.models import Event
        from altaircms.page.models import PageSet

        event = Event(id=id, deal_close=deal_close)
        pageset = PageSet(event=event, id=id)
        return pageset

    def _make_query(self):
        from altaircms.page.models import PageSet        
        from altaircms.event.models import Event
        qs = PageSet.query.filter(Event.id==PageSet.event_id)
        return qs

    def test_it(self):
        from altaircms.models import DBSession

        deal_closes = [datetime(2011, 1, 1),
                       datetime(2011, 2, 1),
                       datetime(2011, 3, 1)]

        ### the order is 1, 3, 2 !!(not 1, 2, 3)
        pgss = [self._make_pageset(id=1, deal_close=deal_closes[0]), 
                self._make_pageset(id=2, deal_close=deal_closes[2]), 
                self._make_pageset(id=3, deal_close=deal_closes[1])
                ]

        DBSession.add_all(pgss)

        not_sorted_qs = self._make_query()
        result = self._callFUT(not_sorted_qs)

        self.assertNotEquals(deal_closes, [p.event.deal_close for p in not_sorted_qs])
        self.assertEquals(deal_closes, [p.event.deal_close for p in result])


class PagePublishTermOnlySearchableTests(unittest.TestCase):
    """ ページが公開期間のもののみ検索に引っかかる
    """
    def tearDown(self):
        import transaction
        transaction.abort()
        from altaircms.models import DBSession
        DBSession.remove()

    def setUp(self):
        import sqlahelper
        self.session = sqlahelper.get_session()

    def _callFUT(self, *args, **kwargs):
        from altairsite.search.searcher import _refine_pageset_only_published_term
        return _refine_pageset_only_published_term(*args, **kwargs)

    @unittest.skip ("* #5609: must fix")
    def test_it(self):
        from altaircms.page.models import Page, PageSet
        
        page = Page(name=u"this-is-searchable", 
                    published=True, 
                    publish_begin=datetime(2000, 1, 1), 
                    publish_end=datetime(2100, 1, 1))
        pageset = PageSet.get_or_create(page)
        
        self.session.add(pageset)

        target = PageSet.query
        result = self._callFUT(target, now=datetime(2012, 5, 5))

        self.assertEquals([pageset], list(result))

    @unittest.skip ("* #5609: must fix")
    def test_pre_publish_term_not_found(self):
        from altaircms.page.models import Page, PageSet
        
        page = Page(name=u"this-is-searchable", 
                    publish_begin=datetime(2000, 1, 1), 
                    publish_end=datetime(2100, 1, 1))
        pageset = PageSet.get_or_create(page)
        
        self.session.add(pageset)

        target = PageSet.query
        result = self._callFUT(target, now=datetime(1999, 9, 9))

        self.assertEquals([], list(result))

    @unittest.skip ("* #5609: must fix")
    def test_post_publish_term_not_found(self):
        from altaircms.page.models import Page, PageSet
        
        page = Page(name=u"this-is-searchable", 
                    publish_begin=datetime(2000, 1, 1), 
                    publish_end=datetime(2100, 1, 1))
        pageset = PageSet.get_or_create(page)
        
        self.session.add(pageset)

        target = PageSet.query
        result = self._callFUT(target, now=datetime(2200, 1, 1))

        self.assertEquals([], list(result))
            

class HotWordSearchTests(unittest.TestCase):
    """ hotwordの検索のテスト
    """

    def tearDown(self):
        import transaction
        transaction.abort()
        from altaircms.models import DBSession
        DBSession.remove()
        from pyramid.testing import tearDown
        tearDown()

    def setUp(self):
        import transaction
        import sqlahelper
        transaction.abort()
        self.session = sqlahelper.get_session()
        from pyramid.testing import setUp
        self.config = setUp()
        self.config.include("altaircms.page.install_pageset_searcher")

    def _callFUT(self, *args, **kwargs):
        from altairsite.search.searcher import search_by_hotword
        return search_by_hotword(*args, **kwargs)

    @unittest.skip ("* #5609: must fix")
    def test_hotword_search_has_event(self):
        """
        hotword - pagetag - pagetag2pageset - pageset
        """
        from altaircms.tag.models import HotWord
        from altaircms.tag.models import PageTag, PageTag2Page
        from altaircms.page.models import PageSet
        from altaircms.event.models import Event        
        from altaircms.auth.models import Organization
        organization = Organization(short_name="test")
        self.session.add(organization)
        self.session.flush()
        self.config.organization = organization

        event = Event(title=u"this-is-bound-event", organization_id=organization.id)
        pageset = PageSet(event=event, organization_id=organization.id)
        pagetag = PageTag(label=u"tag-name-for-hotword", publicp=True, organization_id=organization.id)
        self.session.add(pageset)
        self.session.add(pagetag)
        self.session.flush()

        pagetag2pageset = PageTag2Page(object_id=pageset.id, tag_id=pagetag.id)
        self.session.add(pagetag2pageset)
        self.session.flush()

        hotword = HotWord(name=u"this-is-hotword-name", tag=pagetag, enablep=True, 
                          display_order=1, 
                          term_begin=datetime(1900, 1, 1), term_end=datetime(2100, 1, 1))
        self.session.add(hotword)
        
        self.session.flush()

        request = self.config
        request.allowable = lambda m, qs=None : qs or m.query
        result = self._callFUT(self.config, PageSet.query,  u"this-is-hotword-name")

        self.assertEquals([pageset],  list(result))


    @unittest.skip ("* #5609: must fix")
    def test_hotword_search_hasnt_event(self):
        """ search by hotword but this pageset hasn't event, so matched items is 0

        """
        from altaircms.tag.models import HotWord
        from altaircms.tag.models import PageTag
        from altaircms.tag.models import PageTag2Page
        from altaircms.page.models import PageSet
        from altaircms.auth.models import Organization
        organization = Organization(short_name="test")
        self.session.add(organization)
        self.session.flush()
        self.config.organization = organization

        pageset = PageSet(organization_id=organization.id)
        pagetag = PageTag(label=u"tag-name-for-hotword", publicp=True, organization_id=organization.id)
        pagetag = PageTag(label=u"tag-name-for-hotword", publicp=True)
        self.session.add(pageset)
        self.session.add(pagetag)
        self.session.flush()

        pagetag2pageset = PageTag2Page(object_id=pageset.id, tag_id=pagetag.id)
        self.session.add(pagetag2pageset)
        ## proxyほしい

        hotword = HotWord(name=u"this-is-hotword-name", tag=pagetag, enablep=True, 
                          display_order=1, 
                          term_begin=datetime(1900, 1, 1), term_end=datetime(2100, 1, 1))
        self.session.add(hotword)
        
        self.session.flush()

        request = self.config
        request.allowable = lambda m, qs=None : qs or m.query
        result = self._callFUT(request, PageSet.query,  u"this-is-hotword-name")
        
        ### not found item!!
        self.assertEquals([],  list(result))

if __name__ == "__main__":
    unittest.main()
