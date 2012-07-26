# -*- coding:utf-8 -*-

import unittest
import datetime
import os.path

"""
Page -> Layout
Page.structure{} # widget id
Widget
"""

from altaircms.lib.testutils import functionalTestTearDown

app = None
def setUpModule():
    global app
    import sqlahelper
    from sqlalchemy import create_engine

    DIR = os.path.dirname(os.path.abspath(__file__))

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)

    from altairsite import main
    import altaircms.auth.models
    import altaircms.models
    defaults = {"sqlalchemy.url": "sqlite://", 
                "session.secret": "B7gzHVRUqErB1TFgSeLCHH3Ux6ShtI", 
                "mako.directories": os.path.join(DIR, "templates"), 
                "pyramid_who.config": "usersite_who.ini",  ##
                "altaircms.organization.mapping.json": "altaircms:../../organization.json", 
                "altaircms.backend.url": "localhost:7654", 
                "altaircms.widget.each_organization.settings": "altaircms.plugins:ticketstar-widget-settings.ini", 
                "altairsite.organization.mapping.name": "ticketstar", 
                "altaircms.usrsite.notfound.template": "altaircms:templates/front/errors/ticketstar/notfound.mako",
                "altaircms.usrsite.forbidden.template": "altaircms:templates/front/errors/ticketstar/forbidden.mako",
                "altaircms.asset.storepath": "altaircms:../../data/assets", 
                "altaircms.debug.strip_security": 'true', 
                "altaircms.plugin_static_directory": "altaircms:plugins/static", 
                "altaircms.layout_directory": "."}
    config = defaults.copy()
    app = main({}, **config)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()
    return app


def tearDownModule():
    functionalTestTearDown()


class UseAssetMixin(object):
    def _getImageAsset(self):
        from altaircms.asset.models import ImageAsset
        D = {'filepath': u'/static/img/samples/Abstract_Desktop_290.jpg',
             'id': 1,
             "page_id": 2}
        return ImageAsset.from_dict(D)

    def _getMovieAsset(self):
        from altaircms.asset.models import MovieAsset
        D = {'filepath': u'/static/img/samples/movie.mp4',
             'id': 2,
             "page_id": 2, 
             "mimetype": "video/mp4"}
        return MovieAsset.from_dict(D)

    def _getFlashAsset(self):
        from altaircms.asset.models import FlashAsset
        D = {'filepath': u'/static/img/samples/flash.swf',
             'id': 3,
             "page_id": 2}
        return FlashAsset.from_dict(D)

    def _getFlashAsset2(self):
        from altaircms.asset.models import FlashAsset
        D = {'filepath': u'/static/img/samples/flash.swf',
             'id': 32,
             "page_id": 2}
        return FlashAsset.from_dict(D)

class UseWidgetMixin(object):
    def _getTextWidget(self):
        from altaircms.plugins.widget.freetext.models import FreetextWidget
        D = {'id': 1, 'text': u'freetext',"page_id": 2}
        return FreetextWidget.from_dict(D)

    def _getImageWidget(self):
        from altaircms.plugins.widget.image.models import ImageWidget
        asset = self._getImageAsset()
        D = {"id": 2, "asset": asset,  "asset_id": asset.id}
        return ImageWidget.from_dict(D)

    def _getMovieWidget(self):
        from altaircms.plugins.widget.movie.models import MovieWidget
        asset = self._getMovieAsset()
        D = {"id": 3, "asset": asset,  "asset_id": asset.id}
        return MovieWidget.from_dict(D)

    def _getCalendarWidget(self):
        from altaircms.plugins.widget.calendar.models import CalendarWidget
        from datetime import date
        D = {"id": 4,
             "calendar_type": "term", 
             "from_date": date(2012, 2, 1), 
             "to_date": date(2012, 4, 3), 
             }
        return CalendarWidget.from_dict(D)

    def _getFlashWidget(self):
        from altaircms.plugins.widget.flash.models import FlashWidget
        asset = self._getFlashAsset()
        D = {"id": 5, "asset": asset,  "asset_id": asset.id}
        return FlashWidget.from_dict(D)

    def _getFlashWidget2(self):
        from altaircms.plugins.widget.flash.models import FlashWidget
        asset = self._getFlashAsset2()
        D = {"id": 52, "asset": asset,  "asset_id": asset.id}
        return FlashWidget.from_dict(D)

class UsePageEtcMixin(object):
    def _getPage(self, structure):
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'boo',
             'event_id': None,
             'id': 2,
             'keywords': u'oo',
             'layout_id': 2,
             'parent_id': None,
             'site_id': None,
             'structure': structure, 
             "publish_begin": datetime.datetime(1900, 1, 1), 
             'title': u'fofoo',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'sample_page',
             'version': None}
        return Page.from_dict(D)

    def _getLayout(self):
        from altaircms.layout.models import Layout
        D = {'blocks': u'[["content"],["footer"], ["js_prerender"], ["js_postrender"]]',
             'client_id': None,
             'created_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755523),
             'id': 2,
             'site_id': None,
             'template_filename': u'layout.mako',
             'title': u'simple',
             'updated_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755641)}
        return Layout.from_dict(D)

    
class FunctionalPageRenderingTest(UseAssetMixin, 
                                  UseWidgetMixin, 
                                  UsePageEtcMixin, 
                                  unittest.TestCase):
    def setUp(self):
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_it(self):
        """ functional test front
        """

        """ pageのデータが存在しない場合のレンダリング 404
        """
        self.testapp.get("/sample_page", status=404)

        """ widgetなしページのレンダリング
        """
        session = self._getSession()
        self._addData(session, u"{}")
        session.flush()
        self.testapp.get("/sample_page", status=200)


        """ widgetありページのレンダリング
        """
        structure = u'''
{"content": [{"pk": 1, "name": "freetext"}, {"pk": 3, "name": "movie"}, {"pk": 4, "name": "calendar"}, {"pk": 5, "name": "flash"}, {"pk": 52,  "name": "flash"}],
 "footer": [{"pk": 2, "name": "image"}]}
'''
        from altaircms.page.models import Page
        page = Page.query.first()
        page.structure = structure
        session.add(page)
        self._addWidget(session)
        self._getSession().flush()

        result = self.testapp.get("/sample_page", status=200)
        text = result.text
        ## fixme
        self.assertTrue('class="image-widget"' in text)
        self.assertTrue('class="movie-widget"' in text)
        self.assertTrue('freetext' in text)
        self.assertTrue('class="flash-widget"' in text)
        # self.assertTrue('class="calendar"' in text)

        self.assertTrue("<img" in text)
        self.assertTrue("<embed" in text)
        ## js swfobject
        self.assertTrue("/static/swfobject.js" in text)

    def _addWidget(self, session):
        session.add(self._getTextWidget())
        session.add(self._getImageWidget())
        session.add(self._getMovieWidget())
        session.add(self._getCalendarWidget())
        session.add(self._getFlashWidget())
        session.add(self._getFlashWidget2())
        self._getSession().flush()

        
    def _addData(self, session, structure=u""):
        session.add(self._getPage(structure))
        session.add(self._getLayout())

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

if __name__ == "__main__":
    unittest.main()
