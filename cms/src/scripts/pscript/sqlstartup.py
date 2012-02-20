# -*- coding:utf-8 -*-

## 不思議なコードの書き方なのは、execを呼び出しているせい。
def main():
    from altaircms.models import DBSession
    import transaction

    from contextlib import contextmanager
    @contextmanager
    def block(message):
        try:
            DBSession.remove()
            yield
            transaction.commit()
        except:
            transaction.abort()
            raise

    with block("create client"):
        import altaircms.models as m
        client = m.Client()
        client.name = u"master"
        client.prefecture = u"tokyo"
        client.address = u"000"
        client.email = "foo@example.jp"
        client.contract_status = 0
        DBSession.add(client)


    with block("create page"):
        from altaircms.page.models import Page
        page = Page()
        def set_with_dict(obj, D):
            for k, v in D.items():
                setattr(obj, k, v)
            return obj
        params = {'description': u'boo',
                  'keyword': u'oo',
                  'tags': u'ooo',
                  'url': u'hohohoho',
                  # 'layout_id': 1,
                  'title': u'boo',
                  # 'structure': u'{}'
                  }
        page = set_with_dict(page, params)
        DBSession.add(page)

    with block("create image asset"):
        from altaircms.asset.models import ImageAsset
        imga = ImageAsset("/static/img/samples/Abstract_Desktop_290.jpg")
        DBSession.add(imga)
        imga = ImageAsset("/static/img/samples/2.jpg")
        DBSession.add(imga)
    
    with block("create layout model"):
        from altaircms.layout.models import Layout
        layout0 = Layout()
        layout0.title = "one"
        layout0.template_filename = "1.mako"
        layout0.blocks = '[["content"],["footer"]]'
        layout0.site_id = 1 ##
        layout0.client_id = 1 ##
        DBSession.add(layout0)

    transaction.commit()


def setup():
    from altaircms.models import Base
    Base.metadata.drop_all();
    Base.metadata.create_all();
setup()
main()

