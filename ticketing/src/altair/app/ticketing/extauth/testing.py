def _setup_db(registry, modules=[], echo=False, engine=None):
    from sqlalchemy import create_engine
    from altair.sqlahelper import register_sessionmaker_with_engine, close_global_db_sessions
    from pyramid.path import DottedNameResolver
    import sqlahelper
    from .models import Base

    # for altair.model.Identifier
    try:
        dummy_engine = sqlahelper.get_engine()
    except:
        dummy_engine = None
    if dummy_engine is None:
        sqlahelper.add_engine(create_engine("sqlite://"))

    close_global_db_sessions(registry)

    prev_engine = Base.metadata.bind
    if prev_engine is not None:
        Base.metadata.drop_all(bind=prev_engine)
        prev_engine.dispose()

    if engine is None:
        engine = create_engine("sqlite://")
        if echo:
            warn(DeprecationWarning("_setup_db(echo=...) IS DEPRECATED!! use engine=... instead"))
        engine.echo = echo
    resolver = DottedNameResolver()
    Base.metadata.bind = engine
    for module in modules:
        resolver.resolve(module)
    Base.metadata.create_all(bind=engine)
    for session_name in ['extauth', 'extauth_slave']:
        register_sessionmaker_with_engine(
            registry,
            session_name,
            engine,
            )
    return engine

def _teardown_db(registry):
    import transaction
    transaction.abort()
    from altair.sqlahelper import close_global_db_sessions
    close_global_db_sessions(registry)

