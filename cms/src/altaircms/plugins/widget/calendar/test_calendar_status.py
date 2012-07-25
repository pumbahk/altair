import unittest
import json

class DummyPerformance(object):
    def __init__(self, backend_id=None):
        self.backend_id = backend_id

class CalendarStatusTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.plugins.widget.calendar.api import _get_performance_status
        return _get_performance_status(*args, **kwargs)

    def test_usually(self):
        jsondata = u"""{
          "stocks": [
            {
              "available": 102,
              "assigned": 109,
              "performance_id": 1,
              "id": 306,
              "stock_type_id": 7
            },
            {
              "available": 67,
              "assigned": 71,
              "performance_id": 1,
              "id": 316,
              "stock_type_id": 8
            }
          ]
        }"""

        from altaircms.plugins.widget.calendar.api import CalcResult
        from altaircms.plugins.widget.calendar.api import CalendarStatus
        data = CalcResult(rawdata=json.loads(jsondata))
        request = None
        performance = DummyPerformance(backend_id=1)

        result = self._callFUT(request, data)
        self.assertEquals(result.get_status(performance), CalendarStatus.circle)

    def test_matched_performance_not_found(self): ## this is illegal case
        jsondata = u"""{
          "stocks": [
            {
              "available": 102,
              "assigned": 109,
              "performance_id": 1,
              "id": 306,
              "stock_type_id": 7
            },
            {
              "available": 67,
              "assigned": 71,
              "performance_id": 1,
              "id": 316,
              "stock_type_id": 8
            }
          ]
        }"""

        from altaircms.plugins.widget.calendar.api import CalcResult
        from altaircms.plugins.widget.calendar.api import CalendarStatus
        data = CalcResult(rawdata=json.loads(jsondata))
        request = None
        performance = DummyPerformance(backend_id=2)

        result = self._callFUT(request, data)
        self.assertEquals(result.get_status(performance), CalendarStatus.cross)

    def test_soldout(self):
        jsondata = u"""{
          "stocks": [
            {
              "available": 0,
              "assigned": 109,
              "performance_id": 1,
              "id": 306,
              "stock_type_id": 7
            }
          ]
        }"""

        from altaircms.plugins.widget.calendar.api import CalcResult
        from altaircms.plugins.widget.calendar.api import CalendarStatus
        data = CalcResult(rawdata=json.loads(jsondata))
        request = None
        performance = DummyPerformance(backend_id=1)

        result = self._callFUT(request, data)
        self.assertEquals(result.get_status(performance), CalendarStatus.cross)

    def test_one_stocktype_is_soldout(self):
        jsondata = u"""{
          "stocks": [
            {
              "available": 0,
              "assigned": 10,
              "performance_id": 1,
              "id": 306,
              "stock_type_id": 7
            },
            {
              "available": 8,
              "assigned": 10,
              "performance_id": 1,
              "id": 316,
              "stock_type_id": 8
            }
          ]
        }"""

        from altaircms.plugins.widget.calendar.api import CalcResult
        from altaircms.plugins.widget.calendar.api import CalendarStatus
        data = CalcResult(rawdata=json.loads(jsondata))
        request = None
        performance = DummyPerformance(backend_id=1)

        result = self._callFUT(request, data)
        self.assertEquals(result.get_status(performance), CalendarStatus.triangle)

    def test_less_assigned(self):
        jsondata = u"""{
          "stocks": [
            {
              "available": 2,
              "assigned": 10,
              "performance_id": 1,
              "id": 306,
              "stock_type_id": 7
            },
            {
              "available": 1,
              "assigned": 10,
              "performance_id": 1,
              "id": 316,
              "stock_type_id": 8
            }
          ]
        }"""

        from altaircms.plugins.widget.calendar.api import CalcResult
        from altaircms.plugins.widget.calendar.api import CalendarStatus
        data = CalcResult(rawdata=json.loads(jsondata))
        request = None
        performance = DummyPerformance(backend_id=1)

        result = self._callFUT(request, data)
        self.assertEquals(result.get_status(performance), CalendarStatus.triangle)
        

if __name__ == "__main__":
    unittest.main()
