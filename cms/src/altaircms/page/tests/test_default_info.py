# -*- encoding:utf-8 -*-

import unittest

"""
URL生成時のmappingのテスト(参考:120427_Title・URLルール.xlsx)
"""

def setUpModule():
    import sqlahelper
    from sqlalchemy import create_engine
    import altaircms.page.models
    import altaircms.event.models
    import altaircms.models

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()


def tearDownModule():
    import transaction
    transaction.abort()


class PageDefaultInfoTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.page.models import PageDefaultInfo
        return PageDefaultInfo

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    ## url check
    def test_url_toplevel(self):
        target = self._makeOne(url_fmt=u"/s/%(url)s")
        result = target.url("music")

        self.assertEquals(result, "/s/music")

    def test_url_middle_level(self):
        target = self._makeOne(url_fmt=u"/s/音楽/%(url)s")
        result = target.url(u"邦楽")

        self.assertEquals(result, "/s/%E9%9F%B3%E6%A5%BD/%E9%82%A6%E6%A5%BD")
    
    def test_url_bottom_level(self):
        target = self._makeOne(url_fmt=u"/s/音楽/邦楽/%(url)s")
        result = target.url(u"ポップス・ロックス")

        self.assertEquals(result, "/s/%E9%9F%B3%E6%A5%BD/%E9%82%A6%E6%A5%BD/%E3%83%9D%E3%83%83%E3%83%97%E3%82%B9%E3%83%BB%E3%83%AD%E3%83%83%E3%82%AF%E3%82%B9")
        
    def test_url_music_detail(self):
        target = self._makeOne(url_fmt=u"/s/音楽/クラシック/%(url)s/!SMFHS")
        result = target.url(u"フジコ・ヘミング・ソロ")

        self.assertEquals(result, "/s/%E9%9F%B3%E6%A5%BD/%E3%82%AF%E3%83%A9%E3%82%B7%E3%83%83%E3%82%AF/%E3%83%95%E3%82%B8%E3%82%B3%E3%83%BB%E3%83%98%E3%83%9F%E3%83%B3%E3%82%B0%E3%83%BB%E3%82%BD%E3%83%AD/%21SMFHS")
        import urllib
        self.assertEquals(urllib.unquote(result).decode("utf-8"), u"/s/音楽/クラシック/フジコ・ヘミング・ソロ/!SMFHS")

    ## title check
    ### titleのformatは全て一緒
    def test_title_toplevel(self):
        target = self._makeOne(title_fmt=u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入")
        result = target.title(u"音楽")

        self.assertEquals(u"【楽天チケット】音楽｜公演・ライブのチケット予約・購入", result)

    ### pageset, pageの初期設定
    def test_create_categorytop_pageset(self):
        target = self._makeOne(url_fmt=u"/s/音楽/%(url)s", 
                               title_fmt=u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入")
        result = target.create_pageset(u"邦楽")

        import urllib
        self.assertEquals(u"/s/音楽/邦楽", 
                          urllib.unquote(result.url).decode("utf-8"))

        self.assertEquals(u"邦楽", result.name)

    def test_create_categorytop_page(self):
        target = self._makeOne(url_fmt=u"/s/音楽/%(url)s", 
                               title_fmt=u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入", 
                               keywords=u"this-is-default-keywords", 
                               description=u"this-is-default-description")
        result = target.create_page(u"邦楽")

        import urllib
        self.assertEquals(u"/s/音楽/邦楽", 
                          urllib.unquote(result.url).decode("utf-8"))

        self.assertEquals(u"【楽天チケット】邦楽｜公演・ライブのチケット予約・購入", result.title)

        self.assertEquals(u"this-is-default-keywords", result.keywords)
        self.assertEquals(u"this-is-default-description", result.description)



    def test_create_detail_pageset_url(self):
        target = self._makeOne(url_fmt=u"/s/スポーツ/野球/プロ野球/%(url)s/!SMFHS", 
                               title_fmt=u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入")
        result = target.create_pageset(u"楽天ゴールデンイーグルス")

        import urllib
        self.assertEquals(urllib.unquote(result.url).decode("utf-8"), 
                          u"/s/スポーツ/野球/プロ野球/楽天ゴールデンイーグルス/!SMFHS")
        self.assertEquals(u"楽天ゴールデンイーグルス", result.name)

    def test_create_detail_page_url(self):
        target = self._makeOne(url_fmt=u"/s/スポーツ/野球/プロ野球/%(url)s/!SMFHS", 
                               title_fmt=u"【楽天チケット】%(title)s｜公演・ライブのチケット予約・購入")
        result = target.create_page(u"楽天ゴールデンイーグルス")

        import urllib
        self.assertEquals(urllib.unquote(result.url).decode("utf-8"), 
                          u"/s/スポーツ/野球/プロ野球/楽天ゴールデンイーグルス/!SMFHS")
        self.assertEquals(u"【楽天チケット】楽天ゴールデンイーグルス｜公演・ライブのチケット予約・購入", result.title)

if __name__ == "__main__":
    unittest.main()


