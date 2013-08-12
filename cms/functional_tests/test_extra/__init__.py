# -*- coding:utf-8 -*-
import unittest
from datetime import datetime
import sys
import os

try:
    from functional_tests.utils import get_here, create_api_key, get_pushed_data_from_backend
    from functional_tests import AppFunctionalTests, logout, login, get_registry
    from functional_tests import delete_models, find_form
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__name__), "../../"))
    from functional_tests.utils import get_here, create_api_key, get_pushed_data_from_backend
    from functional_tests import AppFunctionalTests, logout, login, get_registry, get_here
    from functional_tests import delete_models, find_form

# import logging
# logging.basicConfig(level=logging.WARN)

class ExtraAPITests(AppFunctionalTests):
    def test_it(self):
        from altaircms.plugins.widget.performancelist.models import PerformancelistWidget
        from altaircms.plugins.extra.api import get_stockstatus_summary
        from altaircms.plugins.extra.stockstatus import StockStatus
        class request:
            registry = get_registry()
        class event:
            backend_id = 1
            pass
        class widget:
            type = PerformancelistWidget.type
            salessegment = None
            class page:
                organization_id = 1
        result = get_stockstatus_summary(request, event, StockStatus)
        self.assertEquals(result.scores,
                          {8: 812, 9: 759, 10: 2119, 6: 861, 7: 2874})
        self.assertEquals(result.counts,
                          {8: 843, 9: 788, 10: 2144, 6: 892, 7: 2902})


if __name__ == "__main__":
    def setUpModule():
        from functional_tests import get_app
        get_app()
    unittest.main()
