from collections import defaultdict
import unittest


class FindStopAccessor(object):
    def __init__(self, wrapper, d):
        self.wrapper = wrapper
        self.d = d

    def __repr__(self):
        return repr(self.d)

    def __getitem__(self, k):
        return self.d.get(k)

class EmailInfoTraverser(object):
    def __init__(self, target, data, parent=None, accessor_impl=FindStopAccessor):
        self.target = target 
        self.parent = parent
        self.child = None
        self._configured = False
        self._accessor_impl = accessor_impl
        self._data = data ##
        self.data = self._accessor_impl(self, self._data)

    def visit(self):
        if hasattr(self.target, "extra_mailinfo"):
            self.child = getattr(self, "visit_"+(self.target.__class__.__name__))()
            self._configured = True
        return self

    def visit_Event(self):
        org = self.target.organization
        root = self.__class__(org, org.extra_mailinfo, parent=self)
        root.visit()
        return root

    def visit_Organization(self):
        return None

class MailMessageStructureTests(unittest.TestCase):
    def test_simple(self):
        class Organization:
            extra_mailinfo = defaultdict(list)
        traverser = EmailInfoTraverser()
        traverser.visit(Organization())

# class Event:
#     organization = Organization()
#     extra_mailinfo = defaultdict(list)

# traverser = EmailInfoTraverser(Event(), Event().extra_mailinfo)
# print traverser.visit().data
