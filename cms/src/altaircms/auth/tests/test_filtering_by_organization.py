# -*- coding:utf-8 -*-
import unittest
from altaircms.testing import setup_db, teardown_db

def setUpModule():
    setup_db(["altaircms.page.models", 
              "altaircms.event.models", 
              "altaircms.layout.models", 
              "altaircms.widget.models", 
              "altaircms.auth.models"])

def tearDownModule():
    teardown_db()


class FilteringByOrganizationTests(unittest.TestCase):
    def setUp(self):
        import sqlahelper
        self.session = sqlahelper.get_session()

    def tearDown(self):
        self.session.remove()
        import transaction
        transaction.abort()

    def _withDB(self, o):
        self.session.add(o)
        return o

    def test_without_filter(self):
        from altaircms.auth.models import Operator
        from altaircms.auth.models import Organization
        org = self._withDB(Organization(id=1, backend_id=11, short_name="this-is-test"))
        
        op0 = self._withDB(Operator(auth_source="this-is-operator-auth_source"))
        op1 = self._withDB(Operator(organization_id=org.id, auth_source="this-is-operator-auth_source"))

        result = Operator.query.all()

        self.assertEquals(sorted(result), sorted([op0, op1]))

    def test_with_filter(self):
        from altaircms.auth.models import Operator
        from altaircms.auth.models import Organization
        org = self._withDB(Organization(id=1, backend_id=11, short_name="this-is-test"))
        
        op0 = self._withDB(Operator(auth_source="this-is-operator-auth_source"))
        op1 = self._withDB(Operator(organization_id=org.id, auth_source="this-is-operator-auth_source"))

        result = Operator.query.with_transformation(org.inthere())

        self.assertEquals(sorted(result), sorted([op1]))


class FiltererdQueryFromRequestTests(unittest.TestCase):
    def setUp(self):
        import sqlahelper
        self.session = sqlahelper.get_session()

    def tearDown(self):
        self.session.remove()
        import transaction
        transaction.abort()

    def _withDB(self, o):
        self.session.add(o)
        return o

    def _callFUT(self, request, model):
        from altaircms.auth.api import get_allowable_query
        return get_allowable_query(request)(model)

    def test_matched_organization(self):
        from altaircms.auth.models import Operator
        from altaircms.auth.models import Organization

        org = self._withDB(Organization(id=1, backend_id=11, short_name="this-is-test"))
        op = self._withDB(Operator(organization=org, auth_source="this-is-operator-auth_source"))

        self.session.add(op)
        class request(object):
            organization = org
        result = self._callFUT(request, Operator)

        self.assertEqual(list(result.all()), [op])

    def test_unmatched_organization(self):
        from altaircms.auth.models import Operator
        from altaircms.auth.models import Organization

        org = self._withDB(Organization(id=1, backend_id=11, short_name="this-is-test"))
        op = self._withDB(Operator(organization=org, auth_source="this-is-operator-auth_source"))

        self.session.add(op)
        another_org = self._withDB(Organization(id=2, short_name="another", backend_id=22))
        class request(object):
            organization = another_org

        result = self._callFUT(request, Operator)

        self.assertEqual(list(result.all()), [])

if __name__ == "__main__":
    unittest.main()
