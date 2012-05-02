import unittest
from altaircms.models import DBSession

def withDB(obj):
    DBSession.add(obj)
    return obj

class PromotionManagerTest(unittest.TestCase):
    def _makePromotion(self, asset):
        from altaircms.plugins.widget.promotion.models import Promotion
        withDB(Promotion(main_image))

    def test_it(self):
        pass
if __name__ == "__main__":
    unittest.main()
