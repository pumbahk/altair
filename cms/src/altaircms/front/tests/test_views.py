import unittest
import datetime
import os.path

"""
Page -> Layout
Page.structure{} # widget id
Widget
"""

def setUpModule():
    from altaircms.testutils import create_db
    from altaircms.models import DBSession
    DBSession.remove()
    create_db(message="test view create")

def tearDownModule():
    from altaircms.testutils import dropall_db
    dropall_db(message="test view drop")

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

class UseWidgetMixin(object):
    def _getTextWidget(self):
        from altaircms.plugins.widget.freetext.models import FreetextWidget
        D = {'id': 1, 'text': u'hohoho',"page_id": 2}
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

class UsePageEtcMixin(object):
    def _getPage(self, structure):
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'boo',
             'event_id': None,
             'id': 2,
             'keyword': u'oo',
             'layout_id': 2,
             'parent_id': None,
             'site_id': None,
             'structure': structure, 
             'title': u'fofoo',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'sample_page',
             'version': None}
        return Page.from_dict(D)

    def _getLayout(self):
        from altaircms.layout.models import Layout
        D = {'blocks': u'[["content"],["footer"]]',
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
    DIR = os.path.dirname(os.path.abspath(__file__))
    def setUp(self):
        from altaircms import main_app
        app = main_app({}, {"sqlalchemy.url": "sqlite://", 
                            "mako.directories": os.path.join(self.DIR, "templates")+"\n/", 
                            "plugin.static_directory": "altaircms:plugins/static", 
                            "widget.layout_directories": "."})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        import transaction
        transaction.abort()
        self._getSession().remove()
        
    def test_it(self):
        session = self._getSession()
        self._addData(session)

        result = self.testapp.get("/f/publish/sample_page", status=200)
        text = result.text
        ## fixme
        self.assertTrue('class="image-widget"' in text)
        self.assertTrue('class="movie-widget"' in text)
        self.assertTrue('class="freetext-widget"' in text)
        
        self.assertTrue("<img" in text)
        self.assertTrue("<embed" in text)

    def test_it_nodata(self):
        self.testapp.get("/f/publish/sample_page", status=404)

    def _addData(self, session):
        structure = u'''
{"content": [{"pk": 1, "name": "freetext"}, {"pk": 3, "name": "movie"}, {"pk": 4, "name": "calendar"}],
 "footer": [{"pk": 2, "name": "image"}]}
'''
        session.add(self._getPage(structure))
        session.add(self._getLayout())
        session.add(self._getTextWidget())
        session.add(self._getImageWidget())
        session.add(self._getMovieWidget())
        session.add(self._getCalendarWidget())

        import transaction
        transaction.commit()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

if __name__ == "__main__":
    unittest.main()
