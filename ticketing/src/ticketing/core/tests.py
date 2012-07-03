# move it.
import unittest

def setUpModule():
    import sqlahelper
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    import ticketing.core.models
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()

def tearDownModule():
    import transaction
    transaction.abort()


def organization(*args, **kwargs):
    from .models import Organization
    return Organization(*args, **kwargs)

class EventCMSDataTests(unittest.TestCase):
    def _getTarget(self):
        from .models import Event
        return Event

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_data_include_organazation_id(self):
        target = self._makeOne(organization_id=10000)
        result = target._get_self_cms_data()

        self.assertEqual(result["organization_id"], 10000)

if __name__ == "__main__":
    unittest.main()

