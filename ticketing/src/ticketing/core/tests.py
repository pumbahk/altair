# move it.
import unittest

def get_organization(*args, **kwargs):
    from .models import Organization
    return Organization(*args, **kwargs)

class EventCMSDataTests(unittest.TestCase):
    def _getTarget(self):
        from .models import Event
        return Event

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_data_include_organazation_id(self):
        organization = get_organization(id=10000)
        target = self._makeOne(organization=organization)
        result = target._get_self_cms_data()
        self.assertEqual(result["organization_id"], 10000)

if __name__ == "__main__":
    unittest.main()

