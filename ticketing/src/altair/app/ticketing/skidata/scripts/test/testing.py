#! /usr/bin/env python
# coding=utf-8
from pyramid.path import DottedNameResolver
from warnings import warn


def _setup_db(modules=[], echo=False, hook=None, engine=None):
    from sqlalchemy import create_engine
    import sqlahelper
    # remove existing session if exists
    prev_session = sqlahelper.get_session()
    if prev_session is not None:
        prev_session.remove()
    prev_engine = None
    try:
        prev_engine = sqlahelper.get_engine()
    except RuntimeError:
        pass
    prev_base = sqlahelper.get_base()
    if prev_engine is not None:
        if prev_base is not None:
            prev_base.metadata.drop_all(bind=engine)
        prev_engine.dispose()
    sqlahelper.reset()
    sqlahelper._session = prev_session
    sqlahelper.set_base(prev_base)

    if engine is None:
        engine = create_engine("sqlite://")
        if echo:
            warn(DeprecationWarning("_setup_db(echo=...) IS DEPRECATED!! use engine=... instead"))
        engine.echo = echo
    sqlahelper.add_engine(engine)
    resolver = DottedNameResolver()
    base = sqlahelper.get_base()
    base.metadata.bind = engine
    for module in modules:
        resolver.resolve(module)
    base.metadata.create_all(bind=engine)
    if hook is not None:
        hook()
    return sqlahelper


def _teardown_db():
    import transaction
    transaction.abort()
    import sqlahelper
    session = sqlahelper.get_session()
    session.remove()