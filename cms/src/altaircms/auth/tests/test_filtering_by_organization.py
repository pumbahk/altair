# -*- coding:utf-8 -*-
import unittest

def setUpModule():
    import sqlahelper
    from sqlalchemy import create_engine
    import altaircms.page.models
    import altaircms.event.models
    import altaircms.auth.models

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()

def tearDownModule():
    import sqlahelper
    sqlahelper.get_session().remove()
    import transaction
    transaction.abort()

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
        org = self._withDB(Organization(id=1))
        
        op0 = self._withDB(Operator(auth_source="this-is-operator-auth_source"))
        op1 = self._withDB(Operator(organization_id=org.id, auth_source="this-is-operator-auth_source"))

        result = Operator.query.all()

        self.assertEquals(sorted(result), sorted([op0, op1]))

    def test_with_filter(self):
        from altaircms.auth.models import Operator
        from altaircms.auth.models import Organization
        org = self._withDB(Organization(id=1))
        
        op0 = self._withDB(Operator(auth_source="this-is-operator-auth_source"))
        op1 = self._withDB(Operator(organization_id=org.id, auth_source="this-is-operator-auth_source"))

        result = Operator.query.with_transformation(org.inthere())

        self.assertEquals(sorted(result), sorted([op1]))

        
        

if __name__ == "__main__":
    unittest.main()
