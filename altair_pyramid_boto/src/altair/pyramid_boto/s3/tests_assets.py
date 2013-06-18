from mock import Mock
from unittest import TestCase

class DummyCache(object):
    def __init__(self):
        self.cache_entries = {}

    def get(self, key, createfunc=None):
        if key not in self.cache_entries:
            retval = self.cache_entries[key] = createfunc()
        else:
            retval = self.cache_entries[key]
        return retval

class TestS3Retriever(TestCase):
    def setUp(self):
        self._dummy_entry_cache = DummyCache()
        self._dummy_object_cache = DummyCache()

    def _makeTarget(self, bucket):
        from .assets import S3Retriever
        return S3Retriever(
            bucket,
            '/',
            self._dummy_entry_cache,
            self._dummy_object_cache)

    def test_attr_bucket(self):
        try:
            self._makeTarget(None).bucket
            self.assert_(True)
        except:
            self.fail()

    def test_attr_delimiter(self):
        self.assertEquals(self._makeTarget(None).delimiter, '/')

    def test_get_entry_non_prefix(self):
        dummy_bucket = Mock(list=Mock(return_value=[]))
        target = self._makeTarget(dummy_bucket)
        entry = target.get_entry('aaa')
        self.assertEquals(len(self._dummy_entry_cache.cache_entries), 1)
        self.assertEquals(entry['key_or_prefix'], 'aaa')
        self.assertEquals(entry['canonicalized_key_or_prefix'], 'aaa')
        self.assertEquals(entry['keys_under_prefix'], None)

    def test_get_entry_prefix(self):
        from boto.s3.key import Key as S3Key
        from boto.s3.prefix import Prefix as S3Prefix
        def list(key_or_prefix, delimiter):
            if key_or_prefix == 'aaa':
                return [S3Prefix(name='aaa')]
            else:
                return [S3Key(name='bbb')]
        dummy_bucket = Mock(list=list)
        target = self._makeTarget(dummy_bucket)
        entry = target.get_entry('aaa')
        self.assertEquals(len(self._dummy_entry_cache.cache_entries), 1)
        self.assertEquals(entry['key_or_prefix'], 'aaa')
        self.assertEquals(entry['canonicalized_key_or_prefix'], 'aaa/')
        self.assertEquals(entry['keys_under_prefix'], ['bbb'])
