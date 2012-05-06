# -*- coding:utf-8 -*-

from altaircms.models import DBSession
from altaircms.models import Base
import transaction

from contextlib import contextmanager
@contextmanager
def block(message):
    yield

# def setup():
#     Base.metadata.bind.echo = True
#     Base.metadata.drop_all();
#     Base.metadata.create_all();

def main(env, args):
    #setup()
    with block("create client"):
        import altaircms.auth.models as m
        client = m.Client()
        client.id = 1
        client.name = u"master"
        client.prefecture = u"tokyo"
        client.address = u"000"
        client.email = "foo@example.jp"
        client.contract_status = 0
        DBSession.add(client)

    with block("create role model"):
        from altaircms.auth.initial_data import insert_initial_authdata
        insert_initial_authdata()
        
        from altaircms.auth.models import Operator
        debug_user = Operator(auth_source="debug", user_id=1, id=1, role_id=1, screen_name="debug user")
        DBSession.add(debug_user)


    ##
    from . import demo
    demo.add_initial_junk_data()


    ## promotion
    def append_to_json_structure(page, key, data):
        import json
        structure = json.loads(page.structure)
        if structure.get(key) is None:
            structure[key] = []
        structure[key].append(data)
        page.structure = json.dumps(structure)
        return page

    with block("for promotion area"):
        from altaircms.layout.models import Layout
        layout = Layout()
        layout.title = u"プロモーション枠"
        layout.template_filename = "promotion.mako"
        layout.blocks = '[["main"],["sub"]]'
        layout.site_id = 1 ##
        layout.client_id = 1 ##
        DBSession.add(layout)
        DBSession.flush()

        from altaircms.page.models import Page
        D = {'description': u'プロモーション枠',
             'layout_id': layout.id,
             'title': u'プロモーション枠',
             'url': u'promotion',
             "structure": "{}", 
             'version': None}
        page = Page.from_dict(D)
        DBSession.add(page)
        DBSession.flush()
        
        def add_image_widget(page, block_name, asset):
            from pyramid.testing import DummyRequest
            from altaircms.plugins.widget.image.models import ImageWidgetResource
            from altaircms.plugins.widget.image.views import ImageWidgetView
            request = DummyRequest()
            import uuid
            alt = unicode(uuid.uuid4())
            request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id, nowrap=True, alt=alt, href="http://www.example.com"))
            context = ImageWidgetResource(request)
            request.context = context
            r = ImageWidgetView(request).create()
            append_to_json_structure(page, block_name, 
                                     {"name": "image", "pk": r["pk"]})

        from altaircms.asset.models import ImageAsset
        asset = ImageAsset.query.first()
        add_image_widget(page, "main", asset)
        for i in range(15):
            add_image_widget(page, "sub", asset)

    transaction.commit()


