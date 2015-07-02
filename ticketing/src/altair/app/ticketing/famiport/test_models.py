# encoding:utf-8
from unittest import TestCase
import mock
from .testing import _setup_db, _teardown_db
from pyramid.testing import setUp, tearDown


class TestFamiPortEvent(TestCase):
    def setUp(self):
        self.config = setUp()
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                ])
        from altair.sqlahelper import get_global_db_session
        self.session = get_global_db_session(self.config.registry, 'famiport')

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def testSpaceDelimited(self):
        from .models import FamiPortEvent, FamiPortClient, FamiPortPlayguide, FamiPortVenue, FamiPortGenre1, FamiPortGenre2
        event = FamiPortEvent(
            code_1=u'000000',
            code_2=u'0000',
            name_1=u'name_1',
            name_2=u'name_2',
            client=FamiPortClient(
                name=u'チケットスター',
                code=u'000',
                playguide=FamiPortPlayguide(discrimination_code=1),
                prefix=u'XXX'
                ),
            venue=FamiPortVenue(name=u'venue', client_code=u'000000', name_kana=u'ヴェニュー'),
            genre_1=FamiPortGenre1(code=1, name=u'genre1'),
            genre_2=FamiPortGenre2(genre_1_code=1, code=2, name=u'genre2'),
            keywords=[u'a', u'b', u'c'],
            search_code=u'search'
            )
        self.session.add(event)
        self.session.flush()
        _event = self.session.query(FamiPortEvent).filter_by(code_1=u'000000').one()
        self.assertEqual(_event.keywords, [u'a', u'b', u'c'])
        stored_value = list(self.session.bind.execute('SELECT keywords FROM FamiPortEvent WHERE code_1=?', (u'000000', )))[0][0]
        self.assertEqual(stored_value, u'a b c')


class TestScrew(TestCase):
    def test_screw36(self):
        from .models import screw36
        v = screw36(0x0, 0x123456789)
        self.assertEqual(v, 0x123456789)
        v = screw36(0x555555555, 0x123456789)
        self.assertEqual(v, 0xa96156b56 ^ 0x123456789)
        v = screw36(0xaaaaaaaaa, 0x123456789)
        self.assertEqual(v, 0x569ea94a9 ^ 0x123456789)

    def test_screw47(self):
        from .models import screw47
        v = screw47(0x555555555555, 0x12345678901)
        self.assertEqual(v, 0x4d54b5a4ad71 ^ 0x12345678901)
        v = screw47(0x2aaaaaaaaaaa, 0x12345678901)
        self.assertEqual(v, 0x32ab4a5b528e ^ 0x12345678901)


class TestCalculateGtinCd(TestCase):
    def test_it(self):
        from .models import calculate_gtin_cd
        self.assertEqual(calculate_gtin_cd(u'629104150021'), u'3')


class FamiPortInformationMessageTest(TestCase):
    def setUp(self):
        self.config = setUp()
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                ])
        from altair.sqlahelper import get_global_db_session
        self.session = get_global_db_session(self.config.registry, 'famiport')

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def _target(self):
        from .models import FamiPortInformationMessage as klass
        return klass

    def _makeOne(self, *args, **kwargs):
        return self._target()(*args, **kwargs)

    def test_it(self):
        target = self._target()
        kwds = {
            'result_code': 'WithInformation',
            'message': u'日本語のメッセージ',
            }

        old_obj = self._makeOne(**kwds)
        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)

    def test_create(self):
        target = self._target()
        kwds = {
            'result_code': 'WithInformation',
            'message': u'日本語のメッセージ',
            }

        old_obj = target(**kwds)

        self.session.add(old_obj)
        self.session.flush()
        filter_sql = (target.id == old_obj.id)
        new_obj = self.session \
            .query(target) \
            .filter(filter_sql) \
            .one()

        for key, value in kwds.items():
            self.assertEqual(getattr(new_obj, key), value)

    def test_get_message(self):
        from .communication import InformationResultCodeEnum
        target = self._target()
        kwds = {
            'information_result_code': InformationResultCodeEnum.WithInformation,
            'default_message': '',
            'session': self.session,
            }

        msg = target.get_message(**kwds)
        self.assertEqual(msg, '')


class CreateRandomSequenceNumberTest(TestCase):
    def _get_target(self):
        from .models import create_random_sequence_number as target
        return target

    def _get_valid_chars(self):
        import string
        valid_cahrs = string.digits + string.ascii_uppercase
        return valid_cahrs

    def test_it_length_13(self):
        length = 13
        func = self._get_target()
        valid_chars = self._get_valid_chars()
        value = func(length)
        self.assertEqual(length, len(value))
        for ch in value:
            self.assertIn(ch, valid_chars)

    def test_it_length_14(self):
        length = 14
        func = self._get_target()
        valid_chars = self._get_valid_chars()
        value = func(length)
        self.assertEqual(length, len(value))
        for ch in value:
            self.assertIn(ch, valid_chars)


class TestFamiPortReceipt(TestCase):
    def _target(self):
        from .models import FamiPortReceipt as klass
        return klass

    def _makeOne(self, *args, **kwargs):
        return self._target()(*args, **kwargs)

    def test_mark_completed(self):
        from pyramid.testing import DummyRequest
        from datetime import datetime
        now_ = datetime.now()
        request = DummyRequest()
        request.registry = mock.Mock()
        receipt = self._makeOne(
            id=1,
            reserve_number=u'111111111',
            completed_at=None,
            )
        receipt.mark_completed(now_, request)
        self.assertEqual(receipt.completed_at, now_)
        self.assertTrue(request.registry.notify.called)

    def test_mark_completed_error(self):
        from .exc import FamiPortUnsatisfiedPreconditionError
        from pyramid.testing import DummyRequest
        from datetime import datetime
        now_ = datetime.now()
        request = DummyRequest()
        request.registry = mock.Mock()
        receipt = self._makeOne(
            id=1,
            reserve_number=u'111111111',
            completed_at=now_,
            )
        with self.assertRaises(FamiPortUnsatisfiedPreconditionError):
            receipt.mark_completed(now_, request)
