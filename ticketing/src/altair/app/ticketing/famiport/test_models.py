# encoding:utf-8
import unittest
from altair.app.ticketing.testing import _setup_db, _teardown_db

class TestFamiportEvent(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.famiport.models',
            ])

    def tearDown(self):
        _teardown_db()

    def testSpaceDelimited(self):
        from .models import FamiPortEvent, FamiPortClient, FamiPortPlayguide, FamiPortVenue, FamiPortGenre1, FamiPortGenre2
        event = FamiPortEvent(
            code_1=u'000000',
            code_2=u'0000',
            name_1=u'name_1',
            name_2=u'name_2',
            client=FamiPortClient(
                code=u'000',
                playguide=FamiPortPlayguide(discrimination_code=1)
                ),
            venue=FamiPortVenue(name=u'venue', name_kana=u'ヴェニュー'),
            genre_1=FamiPortGenre1(code=u'1', name=u'genre1'),
            genre_2=FamiPortGenre2(code=u'2', name=u'genre2'),
            keywords=[u'a', u'b', u'c'],
            search_code=u'search'
            )
        self.session.add(event)
        self.session.flush()
        _event = self.session.query(FamiPortEvent).filter_by(code_1=u'000000').one()
        self.assertEqual(_event.keywords, [u'a', u'b', u'c'])
        stored_value = list(self.session.bind.execute('SELECT keywords FROM FamiPortEvent WHERE code_1=?', (u'000000', )))[0][0]
        self.assertEqual(stored_value, u'a b c')


