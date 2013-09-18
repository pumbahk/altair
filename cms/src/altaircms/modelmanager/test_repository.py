# -*- coding:utf-8 -*-
import unittest
from collections import namedtuple

class FakeQuery(object):
    def __init__(self, xs):
        self.xs = xs

    def offset(self, i):
        return self.__class__(self.xs[i:])

    def filter_by(self, id):
        xs = [x for x in self.xs if x.id == id]
        return self.__class__(xs)

    def limit(self, N):
        r = []
        try:
            for i in range(N):
                r.append(self.xs[i])
        except:
            return r
        return r

    def get(self, i):
        for x in self.xs:
            if x.id == i:
                return x

class Request:
    def __init__(self, xs):
        self.xs = xs
    def allowable(self, model):
        return FakeQuery(self.xs)

FakeAsset = namedtuple("FakeAsset", "id")
_FakeWidget = namedtuple("FakeWidget", "id")
def FakeWidget(id=None):
    return _FakeWidget(id=id)

class FakeQueryTests(unittest.TestCase):
    def test_it(self):
        target = FakeQuery(range(10))
        self.assertEqual(len(target.xs), 10)
        self.assertEqual(target.limit(3), [0, 1, 2])        

        paged = target.offset(3)
        self.assertEqual(len(paged.xs), 7)
        self.assertEqual(paged.limit(3), [3, 4, 5])

        last_paged = target.offset(9)
        self.assertEqual(len(last_paged.xs), 1)
        self.assertEqual(last_paged.limit(3), [9])

def get_assets(N):
    return [FakeAsset(id=i) for i in range(1, N+1)]    

class AssetRepositoryTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.modelmanager.repository import AssetRepository
        return AssetRepository
        
    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_first__without_selected__page1(self):
        """[1o, 2o, 3o, 4, 5, 6, 7, 8, 9, 10]"""
        request = Request(get_assets(10))
        target = self._makeOne(request, FakeAsset, offset=3)
        result = target.list_of_asset(None, 1)

        self.assertEqual(len(result), 3)
        self.assertEqual([e.id for e in result], [1, 2, 3])

    def test_first__without_selected__page2(self):
        """[1, 2, 3, 4o, 5o, 6o, 7, 8, 9, 10]"""
        request = Request(get_assets(10))
        target = self._makeOne(request, FakeAsset, offset=3)
        result = target.list_of_asset(None, 2)

        self.assertEqual(len(result), 3)
        self.assertEqual([e.id for e in result], [4, 5, 6])
        
    def test_first__without_selected__last(self):
        """[1, 2, 3, 4, 5, 6, 7, 8, 9, 10o]"""
        request = Request(get_assets(10))
        target = self._makeOne(request, FakeAsset, offset=3)
        result = target.list_of_asset(None, 4)

        self.assertEqual(len(result), 1)
        self.assertEqual([e.id for e in result], [10])

    def test_first__with_selected__page1(self):
        """[5o, 1o, 2o, 3, 4, 5, 6, 7, 8, 9, 10]"""
        request = Request(get_assets(10))
        target = self._makeOne(request, FakeAsset, offset=3)
        asset_id = 5
        result = target.list_of_asset(asset_id, 1)

        self.assertEqual(len(result), 3)
        self.assertEqual([e.id for e in result], [5, 1, 2])

    def test_first__with_selected__page2(self):
        """[5, 1, 2, 3o, 4o, 5o, 6, 7, 8, 9, 10]"""
        request = Request(get_assets(10))
        target = self._makeOne(request, FakeAsset, offset=3)
        asset_id = 5
        result = target.list_of_asset(asset_id, 2)

        self.assertEqual(len(result), 3)
        self.assertEqual([e.id for e in result], [3, 4, 5])
        
    def test_first__with_selected__last(self):
        """[5, 1, 2, 3, 4, 5, 6, 7, 8, 9o, 10o]"""
        request = Request(get_assets(10))
        target = self._makeOne(request, FakeAsset, offset=3)
        asset_id = 5
        result = target.list_of_asset(asset_id, 4)

        self.assertEqual(len(result), 2)
        self.assertEqual([e.id for e in result], [9, 10])
        
    def test_filter_query(self):
        request = Request(get_assets(10))
        target = self._makeOne(request, FakeAsset, offset=3)
        result = target.filter_by(id=6).list_of_asset(None, 1)
        
        self.assertEqual(len(result), 1)
        self.assertEqual([e.id for e in result], [6])


class WidgetRepository(unittest.TestCase):
    def _getTarget(self):
        from altaircms.modelmanager.repository import WidgetRepository
        return WidgetRepository
        
    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)
        
    def test_get(self):
        widget = _FakeWidget(id=10)
        request = Request([widget]) 

        target = self._makeOne(request, FakeWidget)
        result = target.get_or_create(10)
        self.assertEqual(result, widget)

    def test_create(self):
        request = Request([]) 

        target = self._makeOne(request, FakeWidget)
        result = target.get_or_create(None)
        self.assertTrue(isinstance(result, _FakeWidget))

    def test_create2(self):
        request = Request([]) 

        target = self._makeOne(request, FakeWidget)
        result = target.get_or_create("null")
        self.assertTrue(isinstance(result, _FakeWidget))


if __name__ == "__main__":
    unittest.main()
