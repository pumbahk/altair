import unittest
import mock

class NervousDictTest(unittest.TestCase):
    def _getTarget(self):
        from .nervous import NervousDict
        return NervousDict

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_new_and_len(self):
        target = self._makeOne()
        self.assertTrue(isinstance(target, self._getTarget()))
        self.assertEqual(len(target), 0)
        target = self._makeOne([(1, 2)])
        self.assertTrue(isinstance(target, self._getTarget()))
        self.assertEqual(len(target), 1)
        target = self._makeOne([(1, 2), (1, 3)])
        self.assertTrue(isinstance(target, self._getTarget()))
        self.assertEqual(len(target), 1)
        target = self._makeOne([(1, 2), (2, 3), (3, 4)])
        self.assertTrue(isinstance(target, self._getTarget()))
        self.assertEqual(len(target), 3)

    def test_setitem(self):
        callback = mock.Mock()
        target = self._makeOne()
        target._bind(callback)
        self.assertFalse(callback.called)
        target['a'] = 'b'
        self.assertEqual(len(target), 1)
        callback.assert_called_with(target)

    def test_delitem(self):
        callback = mock.Mock()
        target = self._makeOne()
        target['a'] = 'b'
        target._bind(callback)
        self.assertFalse(callback.called)
        del target['a']
        self.assertEqual(len(target), 0)
        callback.assert_called_with(target)

    def test_setdefault(self):
        callback = mock.Mock()
        target = self._makeOne()
        target._bind(callback)
        target.setdefault('a', 'b')
        self.assertEqual(len(target), 1)
        callback.assert_called_with(target)


class NervousListTest(unittest.TestCase):
    def _getTarget(self):
        from .nervous import NervousList
        return NervousList

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_new_and_len(self):
        target = self._makeOne()
        self.assertTrue(isinstance(target, self._getTarget()))
        self.assertEqual(len(target), 0)
        target = self._makeOne([1])
        self.assertTrue(isinstance(target, self._getTarget()))
        self.assertEqual(len(target), 1)
        target = self._makeOne([1, 2])
        self.assertTrue(isinstance(target, self._getTarget()))
        self.assertEqual(len(target), 2)
        target = self._makeOne([1, 2, 3])
        self.assertTrue(isinstance(target, self._getTarget()))
        self.assertEqual(len(target), 3)

    def test_append(self):
        callback = mock.Mock()
        target = self._makeOne()
        target._bind(callback)
        self.assertFalse(callback.called)
        target.append('a')
        self.assertEqual(len(target), 1)
        callback.assert_called_with(target)
        target.append('b')
        self.assertEqual(callback.call_count, 2)
        self.assertEqual(len(target), 2)
        callback.assert_called_with(target)

    def test_insert(self):
        callback = mock.Mock()
        target = self._makeOne()
        target._bind(callback)
        self.assertFalse(callback.called)
        target.insert(0, 'a')
        self.assertEqual(len(target), 1)
        callback.assert_called_with(target)
        target.insert(0, 'b')
        self.assertEqual(callback.call_count, 2)
        callback.assert_called_with(target)
        self.assertEqual(len(target), 2)

    def test_setitem(self):
        callback = mock.Mock()
        target = self._makeOne([None])
        target._bind(callback)
        self.assertFalse(callback.called)
        target[0] = 'a'
        self.assertEqual(len(target), 1)
        callback.assert_called_with(target)

    def test_delitem(self):
        callback = mock.Mock()
        target = self._makeOne([None])
        target[0] = 'b'
        target._bind(callback)
        self.assertFalse(callback.called)
        del target[0]
        self.assertEqual(len(target), 0)
        callback.assert_called_with(target)

    def test_setslice(self):
        callback = mock.Mock()
        target = self._makeOne()
        target._bind(callback)
        self.assertFalse(callback.called)
        target[2:] = ['a', 'b', 'c']
        callback.assert_called_with(target)
        self.assertEqual(list(target), ['a', 'b', 'c'])
        target[1:1] = ['d']
        self.assertEqual(list(target), ['a', 'd', 'b', 'c'])


class TestNervousJSONDecoder(unittest.TestCase):
    def _getTarget(self):
        from .nervous import NervousJSONDecoder
        return NervousJSONDecoder

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_empty_obj(self):
        from .nervous import NervousDict, NervousList
        self.assertTrue(isinstance(self._makeOne().decode('{}'), NervousDict))

    def test_non_empty_obj(self):
        from .nervous import NervousDict, NervousList
        result = self._makeOne().decode('{"a":"b"}')
        self.assertTrue(isinstance(result, NervousDict))
        self.assertEqual(len(result), 1)
        self.assertEqual(result['a'], 'b')

    def test_empty_list(self):
        from .nervous import NervousDict, NervousList
        result = self._makeOne().decode('[]')
        self.assertTrue(isinstance(result, NervousList))
        self.assertEqual(len(result), 0)

    def test_non_empty_list(self):
        from .nervous import NervousDict, NervousList
        result = self._makeOne().decode('[1]')
        self.assertTrue(isinstance(result, NervousList))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 1)

    def test_composite(self):
        from .nervous import NervousDict, NervousList
        result = self._makeOne().decode('[[], {"a":{}}]')
        self.assertTrue(isinstance(result, NervousList))
        self.assertTrue(isinstance(result[0], NervousList))
        self.assertTrue(isinstance(result[1], NervousDict))
        self.assertTrue(isinstance(result[1]["a"], NervousDict))

    def test_propagate_composite(self):
        from .nervous import NervousDict, NervousList
        callback = mock.Mock()
        result = self._makeOne().decode('[[], {"a":{}}]')
        result._bind(callback)
        self.assertFalse(callback.called)
        self.assertTrue(isinstance(result, NervousList))
        self.assertTrue(isinstance(result[0], NervousList))
        self.assertTrue(isinstance(result[1], NervousDict))
        self.assertTrue(isinstance(result[1]["a"], NervousDict))
        result[1]["a"]["b"] = 2
        callback.assert_called_with(result[1]["a"])

    def test_binder_unbind(self):
        from .nervous import NervousDict, NervousList
        callback = mock.Mock()
        result = self._makeOne().decode('[[], []]')
        result._bind(callback)
        self.assertFalse(callback.called)
        self.assertTrue(isinstance(result, NervousList))
        self.assertTrue(isinstance(result[0], NervousList))
        self.assertTrue(isinstance(result[1], NervousList))
        a = result.pop()
        callback.assert_called_with(result)
        callback.reset_mock()
        self.assertFalse(callback.called)
        a.append(1)
        self.assertFalse(callback.called)

    def test_binder_weakref(self):
        from .nervous import NervousDict, NervousList
        callback = mock.Mock()
        result = self._makeOne().decode('[[], []]')
        result._bind(callback)
        self.assertFalse(callback.called)
        self.assertTrue(isinstance(result, NervousList))
        self.assertTrue(isinstance(result[0], NervousList))
        self.assertTrue(isinstance(result[1], NervousList))
        a = result[1]
        del result
        callback.reset_mock()
        self.assertFalse(callback.called)
        a.append(1)
        self.assertFalse(callback.called)

    def test_pickle(self):
        from .nervous import NervousDict, NervousList
        import cPickle
        callback = mock.Mock()
        result = self._makeOne().decode('[[1], {"a":"b"}]')
        result2 = cPickle.loads(cPickle.dumps(result))
        self.assertEqual(len(result2), 2)
        self.assertEqual(type(result2), list)
        self.assertEqual(len(result2[0]), 1)
        self.assertEqual(type(result2[0]), list)
        self.assertEqual(result2[0][0], 1)
        self.assertEqual(len(result2[1]), 1)
        self.assertEqual(type(result2[1]), dict)
        self.assertEqual(result2[1]["a"], "b")

