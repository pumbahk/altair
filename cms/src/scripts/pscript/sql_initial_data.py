# -*- coding:utf-8 -*-
## システム稼働に必要な最低限のデータ投入を行う
## 不思議なコードの書き方なのは、execを呼び出しているせい。

def main():
    from altaircms.models import DBSession
    import transaction

    from contextlib import contextmanager
    @contextmanager
    def block(message):
        yield

    with block("create role model"):
        from altaircms.auth.initial_data import insert_initial_authdata
        insert_initial_authdata()

    with block("create layout model"):
        from altaircms.layout.models import Layout
        layout0 = Layout()
        layout0.id = 2
        layout0.title = "two"
        layout0.template_filename = "2.mako"
        layout0.blocks = '[["content"],["footer"]]'
        layout0.site_id = 1 ##
        layout0.client_id = 1 ##
        DBSession.add(layout0)

        layout1 = Layout()
        layout1.id = 1
        layout1.title = "one"
        layout1.template_filename = "1.mako"
        layout1.blocks = '[["content"],["footer"]]'
        layout1.site_id = 1 ##
        layout1.client_id = 1 ##
        DBSession.add(layout1)
    transaction.commit()


def setup():
    from altaircms.models import Base
    Base.metadata.drop_all()
    Base.metadata.create_all()
setup()
main()

