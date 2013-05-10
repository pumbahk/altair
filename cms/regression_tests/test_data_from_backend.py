# -*- coding:utf-8 -*-
import unittest
from pyramid import testing

class DataFromBackendTests(unittest.TestCase):
    def setUp(self):
        from altaircms.testing import setup_db
        setup_db(["altaircms.page.models", 
                  "altaircms.tag.models", 
                  "altaircms.layout.models", 
                  "altaircms.widget.models", 
                  "altaircms.event.models", 
                  "altaircms.asset.models"])

    def tearDown(self):
        from altaircms.testing import teardown_db
        teardown_db()

    def _postFromBackend(self, *args, **kwargs):
        from altaircms.event.api import parse_and_save_event
        return parse_and_save_event(*args, **kwargs)

    def _getOriginalData(self):
        data = {
            "organization": {
                "id": 1, 
                "code": u"DM", 
                "short_name": u"demo"
                }, 
            "created_at": u"2012-06-20T10:33:34", 
            "events": [
                {
                    "organization_id": 1000, 
                    "code": u"DM399", 
                    "subtitle": u"なし", 
                    "title": u"マツイ・オン・アイス", 
                    "performances": [
                        {
                            "end_on": u"2013-03-15T13:00:00", 
                            "start_on": u"2013-03-15T10:00:00", 
                            "name": u"マツイ・オン・アイス(東京公演)", 
                            "open_on": u"2013-03-15T08:00:00", 
                            "prefecture": u"tokyo", 
                            "venue": u"まついZEROホール", 
                            "code": u"this-is-code", 
                            "id": 96, 
                            "sales": [
                                {
                                    "tickets": [], 
                                    "group_id": 1, 
                                    "start_on": u"2012-01-12T10:00:00", 
                                    "kind_name": u"first_lottery", 
                                    "kind_label": u"最速抽選", 
                                    "name": u"最初は抽選のつもりでした", 
                                    "seat_choice": u"false", 
                                    "end_on": u"2012-01-22T10:00:00", 
                                    "id": 39, 
                                    }
                                ]
                            }
                        ], 
                    "id": 20
                    }
                ], 
            "updated_at": u"2012-06-20T10:33:34"
            }
        return data

    def test_3744(self):
        import transaction
        from altaircms.models import SalesSegmentGroup

        data = self._getOriginalData()
        salessegment_data = data["events"][0]["performances"][0]["sales"][0]
        salessegment_data["kind_label"] = u"最速抽選"
        salessegment_data["kind_name"] = u"first_lottery"
        salessegment_data["name"] = u"最初は抽選のつもりでした"
        request = testing.DummyRequest()
        self._postFromBackend(request, data)
        transaction.commit()
        self.assertEquals(SalesSegmentGroup.query.count(), 1)


        salessegment_data = data["events"][0]["performances"][0]["sales"][0]
        salessegment_data["kind_label"] = u"一般先行"
        salessegment_data["kind_name"] = u"early_firstcome"
        salessegment_data["name"] = u"実際には先行販売でした"
        request = testing.DummyRequest()
        self._postFromBackend(request, data)
        transaction.commit()
        self.assertEquals(SalesSegmentGroup.query.count(), 1)

    def test_3745(self):
        import transaction
        from altaircms.models import SalesSegmentGroup

        data = self._getOriginalData()
        performance_data = data["events"][0]["performances"][0]
        performance_data["subtitle"] = u"最初は公演あると思ってました"
        request = testing.DummyRequest()
        self._postFromBackend(request, data)
        transaction.commit()
        self.assertEquals(SalesSegmentGroup.query.count(), 1)


        performance_data["subtitle"] = u"いつの間にか中止になっていました"
        performance_data["delegated"] = "true"
        self._postFromBackend(request, data)
        transaction.commit()
        self.assertEquals(SalesSegmentGroup.query.count(), 0)

if __name__ == "__main__":
    unittest.main()
