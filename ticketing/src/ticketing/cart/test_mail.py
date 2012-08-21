# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing

def setUpModule():
    from ticketing.testing import _setup_db
    _setup_db(modules=[
            "ticketing.models",
            "ticketing.core.models",
            "ticketing.cart.models",
            ])

def tearDownModule():
    from ticketing.testing import _teardown_db
    _teardown_db()

class MailCreateUnitTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_CompletedMailDispacher(self):
        pass
        
if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
