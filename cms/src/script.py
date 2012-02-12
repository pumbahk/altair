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


    # with block("create page"):
    #     from altaircms.page.models import Page
    #     page = m.Page()
    #     def set_with_dict(obj, D):
    #         for k, v in D.items():
    #             setattr(obj, k, v)
    #         return obj
    #     params = {'description': u'boo',
    #               'keyword': u'oo',
    #               'tags': u'ooo',
    #               'url': u'hohohoho',
    #               # 'layout_id': 1,
    #               'title': u'boo',
    #               # 'structure': u'{}'
    #               }
    #     page = set_with_dict(page, params)
    #     session.add(page)

    with block("create image asset"):
        from altaircms.asset.models import ImageAsset
        imga = ImageAsset("/static/img/samples/Abstract_Desktop_290.jpg")
        session.add(imga)
        imga = ImageAsset("/static/img/samples/2.jpg")
        session.add(imga)
    
    with block("create layout model"):
        from altaircms.layout.models import Layout
        layout0 = Layout()
        layout0.title = "one"
        layout0.template_filename = "./altaircms/templates/front/layout/1.mako"
        layout0.blocks = '[["content"],["footer"]]'
        layout0.site_id = 1 ##
        layout0.client_id = 1 ##
        session.add(layout0)

    transaction.commit()

def main(argv):
    if len(argv) < 2:
        sys.exit()
    path = argv[1]
    engine = get_engine(path)
    return use_session(setup_session(engine))

if __name__ == "__main__":
    main(sys.argv)
