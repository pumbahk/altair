import unittest
from pyramid import testing

class MailMessageStructureTests(unittest.TestCase):
    def _getTarget(self):
        from ticketing.mails.traverser import EmailInfoTraverser
        return EmailInfoTraverser

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_onechain(self):
        class Organization:
            extra_mailinfo = testing.DummyResource(data=dict(header="header"))

        target = self._makeOne()
        target.visit(Organization())

        self.assertEquals(target.data["header"], "header")
        self.assertEquals(target.data["footer"], None)

    def test_twochain(self):
        class Organization:
            extra_mailinfo = testing.DummyResource(data=dict(header="organization header", footer="footer"))
        class Event:
            extra_mailinfo = testing.DummyResource(data=dict(header="event header"))
            organization = Organization()

        target = self._makeOne()
        target.visit(Event())

        self.assertEquals(target.data["header"], "event header")
        self.assertEquals(target.data["footer"], "footer")

    def test_threechain(self):
        class Organization:
            extra_mailinfo = testing.DummyResource(data=dict(one="1", two="2", three="O3"))
        class Event:
            extra_mailinfo = testing.DummyResource(data=dict(one="1", two="E2"))
            organization = Organization()
        class Performance:
            extra_mailinfo = testing.DummyResource(data=dict(one="P1"))
            event = Event()
            
        target = self._makeOne()
        target.visit(Performance())

        self.assertEquals(target.data["one"], "P1")
        self.assertEquals(target.data["two"], "E2")
        self.assertEquals(target.data["three"], "O3")

    def test_chainable_if_none(self):
        class Organization:
            extra_mailinfo = testing.DummyResource(data=dict(one="1", two="2", three="O3"))
        class Event:
            extra_mailinfo = None
            organization = Organization()
            
        target = self._makeOne()
        target.visit(Event())

        self.assertEquals(target.data["one"], "1")
        

    def test_getall(self):
        class Organization:
            extra_mailinfo = testing.DummyResource(data=dict(one="1", two="2", three="O3"))
        class Event:
            extra_mailinfo = testing.DummyResource(data=dict(one="1", two="E2"))
            organization = Organization()
        class Performance:
            extra_mailinfo = testing.DummyResource(data=dict(one="P1"))
            event = Event()
            
        target = self._makeOne()
        target.visit(Performance())

        self.assertEquals(target.data.getall("one"), ["P1", "1", "1"])
        self.assertEquals(target.data.getall("two"), ["E2", "2"])
        self.assertEquals(target.data.getall("three"), ["O3"])

    def test_twochain_with_change_access_function(self):
        class Organization:
            extra_mailinfo = testing.DummyResource(
                data={"comp" : dict(header="complete-header", unique="unique"), 
                      "cancel" : dict(header="cancel-header")
                      }
                )
        
        target = self._makeOne(access=lambda d, k, default=None : d["comp"].get(k, default))
        target.visit(Organization())
        self.assertEquals(target.data["header"], "complete-header")

        target = self._makeOne(access=lambda d, k, default=None : d["cancel"].get(k, default) or d["comp"].get(k, default))
        target.visit(Organization())
        self.assertEquals(target.data["header"], "cancel-header")
        self.assertEquals(target.data["unique"], "unique")

if __name__ == "__main__":
    unittest.main()
