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

class PerformancFormTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def setUp(self):
        import sqlahelper
        self.session = sqlahelper.get_session()

    def _getTarget(self):
        from altaircms.slackoff.forms import PerformanceForm
        return PerformanceForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_no_conflict_create(self):
        target = self._makeOne(formdata=MultiDict(backend_id=1))
        self.assertTrue(target.object_validate())

    def test_conflict_create(self):
        from altaircms.models import Performance
        self.session.add(Performance(backend_id=1))

        target = self._makeOne(formdata=MultiDict(backend_id=1))
        result = target.object_validate()

        self.assertFalse(result)

    def test_no_conflict_update_selfdata(self):
        from altaircms.models import Performance
        self.session.add(Performance(backend_id=1))

        obj = Performance(backend_id=1)

        target = self._makeOne(formdata=MultiDict(backend_id=1))
        result = target.object_validate(obj=obj)

        self.assertTrue(result)

    def test_no_conflict_update(self):
        from altaircms.models import Performance
        self.session.add(Performance(backend_id=1))

        obj = Performance(backend_id=1)

        target = self._makeOne(formdata=MultiDict(backend_id=2))
        result = target.object_validate(obj=obj)

        self.assertTrue(result)

    def test_conflict_update(self):
        """ update: not conflict
        """
        from altaircms.models import Performance

        self.session.add(Performance(backend_id=1))
        self.session.add(Performance(backend_id=2))

        obj = Performance(backend_id=1)
        ## 1 -> 2
        target = self._makeOne(formdata=MultiDict(backend_id=2))
        result = target.object_validate(obj=obj)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
