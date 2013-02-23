# -*- coding:utf-8 -*-
import unittest

class TaggedSearchEnvMixin(object):
    @classmethod
    def _getSession(cls):
        from altaircms.models import DBSession
        return DBSession
    @classmethod
    def _makeSearchedObj(cls, **kwargs):
        from altaircms.page.models import PageSet
        return PageSet(**kwargs)
    @classmethod
    def _makeTag(cls, **kwargs):
        from altaircms.tag.models import PageTag
        return PageTag(**kwargs)

    @classmethod
    def tearDownClass(cls):
        import transaction
        transaction.abort()
    
    @classmethod
    def setUpClass(cls):
        session = cls._getSession()
        organization_id = 1

        """
             A
        AA       AB
      AAA AAB  ABA
      という階層関係で。各階層に{x, y, nil}というようなタグを付けたものが存在
        """
        def o(**kwargs):
            v = cls._makeSearchedObj(organization_id=organization_id, **kwargs)
            session.add(v)
            return v

        def t(**kwargs):
            v = cls._makeTag(organization_id=organization_id, publicp=True, **kwargs)
            session.add(v)
            return v
        def st(**kwargs):
            v = cls._makeTag(organization_id=None, publicp=True, **kwargs)
            session.add(v)
            return v

        a_t = st(label=u"a")
        aa_t = st(label=u"aa")
        ab_t = st(label=u"ab")
        aaa_t = st(label=u"aaa")
        aab_t = st(label=u"aab")
        aba_t = st(label=u"aba")

        ## Organization = 1
        organization_id = 1
        # same name of system tag, but this is normal tag.
        samename_t = t(label=u"ab")

        a = o(name=u"a")
        aa = o(name=u"aa")
        ab = o(name=u"ab")
        aaa = o(name=u"aaa")
        aab = o(name=u"aab")
        aba = o(name=u"aba")

        x_a = o(name=u"x_a")
        x_aa = o(name=u"x_aa")
        x_ab = o(name=u"x_ab")
        x_aaa = o(name=u"x_aaa")
        x_aab = o(name=u"x_aab")
        x_aba = o(name=u"x_aba")

        y_a = o(name=u"y_a")
        y_aa = o(name=u"y_aa")
        y_ab = o(name=u"y_ab")
        y_aaa = o(name=u"y_aaa")
        y_aab = o(name=u"y_aab")
        y_aba = o(name=u"y_aba")

        #tag
        x = t(label=u"x")
        y = t(label=u"y")
        
        x_a.tags.append(x)
        x_aa.tags.append(x)
        x_ab.tags.append(x)
        x_aaa.tags.append(x)
        x_aab.tags.append(x)
        x_aba.tags.append(x)

        y_a.tags.append(y)
        y_aa.tags.append(y)
        y_ab.tags.append(y)
        y_aaa.tags.append(y)
        y_aab.tags.append(y)
        y_aba.tags.append(y)

        a.tags.append(a_t); x_a.tags.append(a_t); y_a.tags.append(a_t)
        aa.tags.append(aa_t); x_aa.tags.append(aa_t); y_aa.tags.append(aa_t)
        aa.tags.append(a_t); x_aa.tags.append(a_t); y_aa.tags.append(a_t)
        ab.tags.append(ab_t); x_ab.tags.append(ab_t); y_ab.tags.append(ab_t)
        ab.tags.append(a_t); x_ab.tags.append(a_t); y_ab.tags.append(a_t)
        aaa.tags.append(aaa_t); x_aaa.tags.append(aaa_t); y_aaa.tags.append(aaa_t)
        aaa.tags.append(a_t); x_aaa.tags.append(a_t); y_aaa.tags.append(a_t)
        aaa.tags.append(aa_t); x_aaa.tags.append(aa_t); y_aaa.tags.append(aa_t)
        aab.tags.append(aab_t); x_aab.tags.append(aab_t); y_aab.tags.append(aab_t)
        aab.tags.append(aa_t); x_aab.tags.append(aa_t); y_aab.tags.append(aa_t)
        aab.tags.append(a_t); x_aab.tags.append(a_t); y_aab.tags.append(a_t)
        aba.tags.append(aba_t); x_aba.tags.append(aba_t); y_aba.tags.append(aba_t)
        aba.tags.append(ab_t); x_aba.tags.append(ab_t); y_aba.tags.append(ab_t)
        aba.tags.append(a_t); x_aba.tags.append(a_t); y_aba.tags.append(a_t)

        a.tags.append(samename_t); x_a.tags.append(samename_t); y_a.tags.append(samename_t)
        aba.tags.append(samename_t); x_aba.tags.append(samename_t); y_aba.tags.append(samename_t)

        ## organization = 2
        organization_id = 2
        # same name of system tag, but this is normal tag.
        samename_t = t(label=u"ab")

        a = o(name=u"a")
        aa = o(name=u"aa")
        ab = o(name=u"ab")
        aaa = o(name=u"aaa")
        aab = o(name=u"aab")
        aba = o(name=u"aba")

        x_a = o(name=u"x_a")
        x_aa = o(name=u"x_aa")
        x_ab = o(name=u"x_ab")
        x_aaa = o(name=u"x_aaa")
        x_aab = o(name=u"x_aab")
        x_aba = o(name=u"x_aba")

        y_a = o(name=u"y_a")
        y_aa = o(name=u"y_aa")
        y_ab = o(name=u"y_ab")
        y_aaa = o(name=u"y_aaa")
        y_aab = o(name=u"y_aab")
        y_aba = o(name=u"y_aba")
        #tag
        x = t(label=u"x")
        y = t(label=u"y")
        
        x_a.tags.append(x)
        x_aa.tags.append(x)
        x_ab.tags.append(x)
        x_aaa.tags.append(x)
        x_aab.tags.append(x)
        x_aba.tags.append(x)

        y_a.tags.append(y)
        y_aa.tags.append(y)
        y_ab.tags.append(y)
        y_aaa.tags.append(y)
        y_aab.tags.append(y)
        y_aba.tags.append(y)

        a.tags.append(a_t); x_a.tags.append(a_t); y_a.tags.append(a_t)
        aa.tags.append(aa_t); x_aa.tags.append(aa_t); y_aa.tags.append(aa_t)
        aa.tags.append(a_t); x_aa.tags.append(a_t); y_aa.tags.append(a_t)
        ab.tags.append(ab_t); x_ab.tags.append(ab_t); y_ab.tags.append(ab_t)
        ab.tags.append(a_t); x_ab.tags.append(a_t); y_ab.tags.append(a_t)
        aaa.tags.append(aaa_t); x_aaa.tags.append(aaa_t); y_aaa.tags.append(aaa_t)
        aaa.tags.append(a_t); x_aaa.tags.append(a_t); y_aaa.tags.append(a_t)
        aaa.tags.append(aa_t); x_aaa.tags.append(aa_t); y_aaa.tags.append(aa_t)
        aab.tags.append(aab_t); x_aab.tags.append(aab_t); y_aab.tags.append(aab_t)
        aab.tags.append(aa_t); x_aab.tags.append(aa_t); y_aab.tags.append(aa_t)
        aab.tags.append(a_t); x_aab.tags.append(a_t); y_aab.tags.append(a_t)
        aba.tags.append(aba_t); x_aba.tags.append(aba_t); y_aba.tags.append(aba_t)
        aba.tags.append(ab_t); x_aba.tags.append(ab_t); y_aba.tags.append(ab_t)
        aba.tags.append(a_t); x_aba.tags.append(a_t); y_aba.tags.append(a_t)

        a.tags.append(samename_t); x_a.tags.append(samename_t); y_a.tags.append(samename_t)
        aba.tags.append(samename_t); x_aba.tags.append(samename_t); y_aba.tags.append(samename_t)

class PageSearchLowerLevelTest(TaggedSearchEnvMixin, unittest.TestCase):
    def test_all_object(self):
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        self.assertEqual(O.query.count(), 6*3*2)

    def test_x_labeld_object(self):
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(T.label==u"x").count(), 6*2)

    def test_x_labeld_object_in_same_organization(self):
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(O.organization_id==T.organization_id).filter(T.label==u"x").count(), 6*2)

    def test_x_labeld_object_in_organization_1(self):
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(O.organization_id==T.organization_id, O.organization_id==1, T.organization_id==1).filter(T.label==u"x").count(), 6)
   
    ## system tag
    def test_systemtag_ab__this_is_invalid_query(self):
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        ## system tag ab -> {ab,  aba}
        ## normal tag ab -> {aba,  a}
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(T.label==u"ab").count(), 2*3*2+3*2*2)

    def test_systemtag_a(self):
        ## system tag a -> {a, aa, ab, aaa, aab, aba}
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(T.label==u"a", T.organization_id==None).count(), 6*3*2)

    def test_systemtag_ab(self):
        ## system tag ab -> {ab,  aba}
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(T.label==u"ab", T.organization_id==None).count(), 2*3*2)

    def test_labeld_ab(self):
        ## normal tag ab -> {aba,  a}
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(T.label==u"ab", T.organization_id==O.organization_id).count(), 3*2*2)

    ## use normal tag and system tag
    def test_labeld_ab_and_system_tag_ab__invalid_query(self):
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(T.label==u"ab", O.organization_id==T.organization_id).filter(T.organization_id==None).count(), 0)

    def test_labeld_ab_and_system_tag_ab(self):
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        import sqlalchemy.orm as orm
        x = orm.aliased(X)
        t = orm.aliased(T)
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(O.id==x.object_id, x.tag_id==t.id).filter(T.label==u"ab", O.organization_id==T.organization_id).filter(t.label==u"ab", t.organization_id==None).count(), 3*2)

    def test_labeld_ab_and_system_tag_ab_in_organization_1(self):
        from altaircms.page.models import PageSet as O, PageTag as T, PageTag2Page as X
        import sqlalchemy.orm as orm
        x = orm.aliased(X)
        t = orm.aliased(T)
        self.assertEqual(O.query.filter(O.id==X.object_id, X.tag_id==T.id).filter(O.id==x.object_id, x.tag_id==t.id).filter(T.label==u"ab", O.organization_id==T.organization_id).filter(t.label==u"ab", t.organization_id==None).filter(O.organization_id==1, T.organization_id==1).count(), 3)

class PageSearchHigherLevelTest(TaggedSearchEnvMixin, unittest.TestCase):
    def _makeSearcherTag(self):
        from altaircms.tag.manager import TagManager
        from altaircms.page.models import PageSet
        from altaircms.tag import models as m
        return TagManager(Object=PageSet, XRef=m.PageTag2Page, Tag=m.PageTag)

    def _makeSearcherSystemTag(self):
        from altaircms.tag.manager import SystemTagManager
        from altaircms.page.models import PageSet
        from altaircms.tag import models as m
        return SystemTagManager(Object=PageSet, XRef=m.PageTag2Page, Tag=m.PageTag)

    def test_x_labeld_object_in_organization_1(self):
        t_searcher = self._makeSearcherTag()
        tag = t_searcher.get_or_create_tag(u"x", organization_id=1)
        self.assertEqual(t_searcher.search_by_tag(tag).count(), 6)

    def test_system_tag_ab(self):
        st_searcher = self._makeSearcherSystemTag()
        st_tag = st_searcher.get_or_create_tag(u"ab")
        self.assertIsNone(st_tag.organization_id)
        self.assertEqual(st_searcher.search_by_tag(st_tag).count(), 2*3*2)

        #取得したobjectにObject.organization_id==request.organization.idでの絞り込みが必要。
        #これはrequest.allowableの仕事
        # self.assertEqual(st_searcher.search_by_tag(st_tag).filter_by(organization_id=1).count(), 2*3)

    def test_labeld_ab_and_system_tag_ab_in_organization_1(self):
        t_searcher = self._makeSearcherTag()
        tag = t_searcher.get_or_create_tag(u"ab", organization_id=1)
        st_searcher = self._makeSearcherSystemTag()
        st_tag = st_searcher.get_or_create_tag(u"ab")

        self.assertEqual(st_searcher.more_filter_by_tag(t_searcher.search_by_tag(tag), st_tag).count(), 3)

    def test_labeld_ab_and_system_tag_ab_in_organization_1_another(self):
        t_searcher = self._makeSearcherTag()
        tag = t_searcher.get_or_create_tag(u"ab", organization_id=1)
        st_searcher = self._makeSearcherSystemTag()
        st_tag = st_searcher.get_or_create_tag(u"ab")

        self.assertEqual(t_searcher.more_filter_by_tag(st_searcher.search_by_tag(st_tag), tag).count(), 3)

    def test_system_tag_a_and_ab(self):
        st_searcher = self._makeSearcherSystemTag()
        st_tag = st_searcher.get_or_create_tag(u"a")
        st_tag2 = st_searcher.get_or_create_tag(u"ab")
        self.assertEqual(st_searcher.search_by_tag(st_tag).count(), 6*3*2)
        self.assertEqual(st_searcher.more_filter_by_tag(st_searcher.search_by_tag(st_tag), st_tag2).count(), 2*3*2)
        self.assertEqual(st_searcher.more_filter_by_tag(st_searcher.search_by_tag(st_tag2), st_tag).count(), 2*3*2)        


    def test_system_tag_ab_and_labeld_x_and_labeld_ab_in_organization_1(self):
        t_searcher = self._makeSearcherTag()
        tag_ab = t_searcher.get_or_create_tag(u"ab", organization_id=1)
        tag_x = t_searcher.get_or_create_tag(u"x", organization_id=1)
        st_searcher = self._makeSearcherSystemTag()
        st_tag_ab = st_searcher.get_or_create_tag(u"ab")

        result = t_searcher.more_filter_by_tag(
            t_searcher.more_filter_by_tag(
                st_searcher.search_by_tag(st_tag_ab), tag_x), 
            tag_ab).filter_by(organization_id=1)

        self.assertEqual(result.count(), 1)
        

if __name__ == "__main__":
    from altaircms.tag.tests import setUpModule as S
    S()
    unittest.main()
