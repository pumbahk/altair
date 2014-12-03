from pyramid.path import DottedNameResolver
from pyramid.testing import DummyRequest as _DummyRequest
from pyramid.interfaces import IRequest, IRequestExtensions
from pyramid.util import InstancePropertyMixin
from zope.interface import alsoProvides

def _setup_db(modules=[], echo=False):
    resolver = DottedNameResolver()
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///")
    engine.echo = echo
    import sqlahelper
    # remove existing session if exists
    sqlahelper.get_session().remove() 
    sqlahelper.add_engine(engine)
    for module in modules:
        resolver.resolve(module)
    base = sqlahelper.get_base()
    base.metadata.drop_all()
    base.metadata.create_all()
    return sqlahelper.get_session()

def _teardown_db():
    import transaction
    transaction.abort()
    import sqlahelper
    session = sqlahelper.get_session()
    session.remove()

class DummyRequest(_DummyRequest):
    def __init__(self, *args, **kwargs):
        super(DummyRequest, self).__init__(*args, **kwargs)
        from webob.multidict import MultiDict
        if hasattr(self, 'params'):
            self.params = MultiDict(self.params)
        if hasattr(self, 'GET'):
            self.GET = MultiDict(self.GET)
        if hasattr(self, 'POST'):
            self.POST = MultiDict(self.POST)
        self.browserid = kwargs.get("browserid")
        self.request_iface = kwargs.get('request_iface', IRequest)

    def __getattr__(self, k):
        extensions = self.registry.queryUtility(IRequestExtensions)
        if extensions is not None:
            self._set_extensions(extensions)
        if not hasattr(self.__class__, k):
            raise AttributeError(k)
        return getattr(self, k)

    def copy(self):
        return self.__class__(
            params=self.params.copy() if self.params is not None else None,
            environ=self.environ.copy() if self.environ is not None else None,
            headers=self.headers.copy() if self.headers is not None else None,
            path=self.path,
            cookies=self.cookies.copy() if self.cookies is not None else None,
            post=self.POST,
            **dict((k, v) for k, v in self.__dict__.items() if k not in ('params', 'environ', 'headers', 'path', 'cookies', 'post'))
            )


class ElementTreeTestMixin(object):
    def assertEqualsEtree(self, result, expected, msg):
        from lxml.doctestcompare import LXMLOutputChecker
        checker = LXMLOutputChecker()
        if hasattr(result, 'getroot'):
            result = result.getroot()
        if hasattr(expected, 'getroot'):
            expected = expected.getroot()
        self.assertTrue(checker.compare_docs(expected, result), msg)

class SetUpTearDownManager(object):
    def __init__(self, setup=None, teardown=None):
        self.setup = setup
        self.teardown = teardown

    def __enter__(self):
        self.setup and self.setup()

    def __exit__(self, exc, val, tb):
        self.teardown and self.teardown()
        if exc is not None:
            return None
        return True
