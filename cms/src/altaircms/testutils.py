def create_db(echo=False, base=None, session=None):
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///')
    engine.echo = echo
    if base is None or session is None:
        from altaircms import models as m
        m.DBSession.remove()
        m.DBSession.configure(bind=engine)
        m.Base.metadata.create_all(bind=engine)
        return m.DBSession
    else:
        session.configure(bind=engine)
        base.metadata.bind = engine
        base.metadata.create_all(bind=engine)
        return session

def dropall_db(base=None, session=None):
    if base is None or session is None:
        from . import models as m
        m.Base.metadata.drop_all(bind=m.DBSession.bind)
        m.Base.metadata.clear()
    else:
        base.metadata.drop_all(bind=session.bind)
        base.metadata.clear()
