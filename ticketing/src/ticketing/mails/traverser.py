import functools

class FindStopAccessor(object):
    default_access = staticmethod(lambda d, k, default=None: d.get(k, default))
    def __init__(self, wrapper, d, access=None, default=None):
        self.wrapper = wrapper
        self.d = d
        self.default = default
        self.access = access or self.default_access

    def __repr__(self):
        return repr(self.d)

    def _get_failback(self, k):
        chained = self.wrapper.chained
        if chained:
            return chained.data[k]

    def __getitem__(self, k):
        if self.d is None:
            return self.default
        return self.access(self.d, k, default=self.default) or self._get_failback(k)

    def getall(self, k):
        r = []
        this = self.wrapper
        while this:
            v = self.access(this.data.d, k, default=self.default)
            if v:
                r.append(v)
            this = this.chained
        return r

class EmailInfoTraverser(object):
    def __init__(self, accessor_impl=FindStopAccessor, access=None, default=None):
        self.chained = None
        self.target = None
        self._configured = False
        if access or default:
            self._accessor_impl = functools.partial(accessor_impl, access=access, default=default)
        else:
            self._accessor_impl = accessor_impl

    def visit(self, target):
        if not self._configured:
            getattr(self, "visit_"+(target.__class__.__name__))(target)
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
