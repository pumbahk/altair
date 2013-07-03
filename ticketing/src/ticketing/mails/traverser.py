import functools
import logging
from zope.interface import implementer
from .interfaces import ITraverser

logger = logging.getLogger(__name__)

class FindStopAccessor(object):
    default_access = staticmethod(lambda d, k, default=None: d.get(k, default))
    def __init__(self, wrapper, d, access=None, default=None):
        self.wrapper = wrapper
        self.d = d
        self.default = default
        self.access = access or self.default_access

    def __repr__(self):
        return "<{0}:{1}>".format(self.__class__, repr(self.d))

    def _find_next(self, k):
        chained = self.wrapper.chained
        while chained:
            if chained.data:
                break
            chained = chained.chained
        if not chained:
            return self.default
        return chained.data[k]

    def __getitem__(self, k):
        if self.d is None:
            return self._find_next(k)
        return self.access(self.d, k, default=self.default) or self._find_next(k)
    get = __getitem__


    def chained_iter(self):
        this = self.wrapper
        while this:
            if this.data.d:
                yield this
            this = this.chained
            if not this:
                break

    def getall(self, k):
        r = []
        for this in self.chained_iter():
            v = self.access(this.data.d, k, default=self.default)
            if v:
                r.append(v)
        return r

    def exists_at_least_one(self):
        for this in self.chained_iter():
            if self.access.touch(this.data.d):
                return True
        return False

@implementer(ITraverser)
class EmailInfoTraverser(object):
    def __init__(self, accessor_impl=FindStopAccessor, access=None, default=None):
        self.chained = None
        self.target = None
        self._configured = False
        if access or default:
            self._accessor_impl = functools.partial(accessor_impl, access=access, default=default)
        else:
            self._accessor_impl = accessor_impl

    def exists_at_least_one(self):
        if not self._configured:
            raise Exception("this is not configured. this method be enable after visiting anything.")
        return self.data.exists_at_least_one()

    def visit(self, target):
        if not self._configured:
            try:
                visit_method = getattr(self, "visit_"+(target.__class__.__name__))
            except AttributeError:
                visit_method = self.visit_Missing
            visit_method(target)
            self._configured = True
        return self

    def _set_data(self, mailinfo):
        self._data = mailinfo
        self.data = self._accessor_impl(self, mailinfo.data if mailinfo else None)

    def visit_Performance(self, performance):
        event = performance.event
        self.target = performance
        self._set_data(performance.extra_mailinfo)

        root = self.__class__(accessor_impl=self._accessor_impl)
        self.chained = root 
        root.visit(event)

    def visit_Event(self, event):
        organization = event.organization
        self.target = event
        self._set_data(event.extra_mailinfo)

        root = self.__class__(accessor_impl=self._accessor_impl)
        self.chained = root 
        root.visit(organization)

    def visit_Organization(self, organization):
        self.target = organization
        self._set_data(organization.extra_mailinfo)
        
    def visit_Missing(self, target):
        logger.debug("---- missing --- %s" % target)
        self.target = target
        self._set_data(None)

    def visit_FakeObject(self, target):
        self.visit(target._fake_root)
