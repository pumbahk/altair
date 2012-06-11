# -*- encoding:utf-8 -*-
import unittest

from pyramid import testing

import altaircms.models
import altaircms.page.models
import altaircms.event.models
from altaircms.plugins.widget.freetext import models


def setUpModule():
    import transaction
    transaction.abort()

def create_page(*args, **kwargs):
    from altaircms.page.models import Page
    return Page(*args, **kwargs)

def get_session():
    from altaircms.models import DBSession
    return DBSession

class FreeTextWidgetCloneTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    
    def _getTarget(self):
        from altaircms.plugins.widget.freetext.models import FreetextWidget
        return FreetextWidget

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_it(self):
        target = self._makeOne(text=u"this-is-data-of-text-widget", id=1)

        session = get_session()
        result = target.clone(session)

        self.assertNotEquals(result.id, target.id)
        self.assertEquals(result.text, u"this-is-data-of-text-widget")

if __name__ == "__main__":
    unittest.main()

