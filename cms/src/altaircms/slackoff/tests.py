# -*- encoding:utf-8 -*-
import unittest
from webob.multidict import MultiDict

def setUpModule():
    import sqlahelper
    import altaircms.models
    import altaircms.page.models
    import sqlalchemy as sa
    import altaircms.page.models
    import altaircms.models
    import altaircms.tag.models
    import altaircms.topic.models

    engine = sa.create_engine("sqlite://")
    sqlahelper.add_engine(engine)
    session = sqlahelper.get_session()
    session.remove()
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()

class PerformancBackendIdConflictTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.slackoff.forms import PerformanceForm
        return PerformanceForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_no_conflict_create(self):
        """ create: not conflict
        """
        form = self._makeOne(formdata=MultiDict(backend_id=1))
        self.assertTrue(form.object_validate())

    def test_conflict_create(self):
        """ create: not conflict
        """
        from altaircms.models import Performance
        import sqlahelper
        session = sqlahelper.get_session()
        session.add(Performance(backend_id=1))

        form = self._makeOne(formdata=MultiDict(backend_id=1))
        result = form.object_validate()

        self.assertFalse(result)

    def test_no_conflict_update_selfdata(self):
        """ update: not conflict
        """
        from altaircms.models import Performance
        import sqlahelper
        session = sqlahelper.get_session()
        session.add(Performance(backend_id=1))

        form = self._makeOne(formdata=MultiDict(backend_id=1))
        obj = Performance(backend_id=1)
        self.assertTrue(form.object_validate(obj=obj))

    def test_no_conflict_unmatched_parms(self):
        """ update: not conflict
        """
        from altaircms.models import Performance
        import sqlahelper
        session = sqlahelper.get_session()
        session.add(Performance(backend_id=1))

        form = self._makeOne(formdata=MultiDict(backend_id=2))
        obj = Performance(backend_id=1)
        self.assertTrue(form.object_validate(obj=obj))

    def test_conflict_update(self):
        """ update: not conflict
        """
        from altaircms.models import Performance
        import sqlahelper
        session = sqlahelper.get_session()
        session.add(Performance(backend_id=1))
        session.add(Performance(backend_id=2))

        ## 1 -> 2
        form = self._makeOne(formdata=MultiDict(backend_id=2))
        obj = Performance(backend_id=1)
        self.assertFalse(form.object_validate(obj=obj))



if __name__ == "__main__":
    unittest.main()
