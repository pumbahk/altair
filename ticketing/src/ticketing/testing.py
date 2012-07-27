from pyramid.path import DottedNameResolver

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
