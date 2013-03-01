from pyramid.path import DottedNameResolver
from pyramid.testing import DummyRequest as _DummyRequest

def _setup_db(modules=[], echo=False):
    from .logicaldeleting import install
    install()
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
