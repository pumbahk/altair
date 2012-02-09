from pyramid.paster import bootstrap
import sqlalchemy as sa
import sys
import transaction

def get_engine(path):
    env = bootstrap(path)
    return sa.engine_from_config(env["registry"].settings)    

def setup_session(engin, clean=True):
    import altaircms.models as m
    m.Base.metadata.drop_all();
    m.Base.metadata.create_all();
    return m.DBSession()    

from contextlib import contextmanager
@contextmanager
def block(message):
    yield
    
def use_session(session):
    session.flush()

    with block("create client"):
        import altaircms.models as m
        client = m.Client()
        client.name = u"master"
        client.prefecture = u"tokyo"
        client.address = u"000"
        client.email = "foo@example.jp"
        client.contract_status = 0
        session.add(client)

        
    with block("create image asset"):
        from altaircms.asset.models import ImageAsset
        imga = ImageAsset("/static/img/samples/Abstract_Desktop_290.jpg")
        session.add(imga)
    
    with block("create layout model"):
        from altaircms.layout.models import Layout
        layout0 = Layout()
        layout0.title = "col2"
        layout0.template_filename = "/static/css/samples/col2.css"
        layout0.site_id = 1 ##
        layout0.client_id = 1 ##
        session.add(layout0)

        layout1 = Layout()
        layout1.title = "col3"
        layout1.template_filename = "/static/css/samples/col3.css"
        layout1.site_id = 1 ##
        layout1.client_id = 1 ##
        session.add(layout1)

    transaction.commit()

def main(argv):
    if len(argv) < 2:
        sys.exit()
    path = argv[1]
    engine = get_engine(path)
    return use_session(setup_session(engine))

if __name__ == "__main__":
    main(sys.argv)
