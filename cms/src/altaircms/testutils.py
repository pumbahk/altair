def create_db(echo=False):
    from altaircms import models as m
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///')
    engine.echo = echo
    m.DBSession.remove()
    m.DBSession.configure(bind=engine)
    m.Base.metadata.create_all(bind=engine)
    return m.DBSession

def dropall_db():
    from . import models as m
    m.Base.metadata.drop_all(bind=m.DBSession.bind)
