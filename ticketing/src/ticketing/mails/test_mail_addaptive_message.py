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
        from ticketing.core.models import MailStatusEnum
        class Organization:
            extra_mailinfo = testing.DummyResource(
                data={MailStatusEnum.CompleteMail : dict(header="complete-header"), 
                      MailStatusEnum.PurchaseCancelMail: dict(header="cancel-header")
                      }
                )
        
        target = self._makeOne(access=lambda d : d[MailStatusEnum.CompleteMail])
        target.visit(Organization())
        self.assertEquals(target.data["header"], "complete-header")

        target = self._makeOne(access=lambda d : d[MailStatusEnum.PurchaseCancelMail])
        target.visit(Organization())
        self.assertEquals(target.data["header"], "cancel-header")

if __name__ == "__main__":
    unittest.main()
