# -*- coding:utf-8 -*-
"""insert category master

Revision ID: b5ecfbf167f
Revises: 137096ec0baa
Create Date: 2012-05-09 16:11:36.812424

"""

# revision identifiers, used by Alembic.
revision = 'b5ecfbf167f'
down_revision = '48e82f3702e3'

from alembic import op
import sqlalchemy as sa

import sqlahelper
from altaircms.models import Category, Site
from altaircms.auth.models import Client

DBSession = sqlahelper.get_session()

class Node(dict):
    def __init__(self, root, children=None):
        self.root = root
        self.children = children or []

    def add(self, x):
        new_node = Node(x)
        self.children.append(new_node)
        return new_node

    def add_session(self, session):
        if self.root:
            session.add(self.root)
        for node in self.children:
            node.add_session(session)

def _create_materials():
    ## site作ってなかった。
    client = Client(
        id = 1,
        name = u"master",
        prefecture = u"tokyo",
        address = u"000",
        email = "foo@example.jp",
        contract_status = 0
        )

    site = Site(name=u"ticketstar",
                description=u"ticketstar ticketstar",
                url="http://example.com",
                client=client)

    DBSession.add(client)
    DBSession.add(site)
    return site, client

def _create_categories(site):
   
    root = Node(None)
    ## トップページ
    lnode = root.add(Category(site=site, hierarchy=u"大", name=u"チケットトップ", label="index", orderno=0, 
                              imgsrc="/static/ticketstar/img/common/header_nav_top.gif"))

    ## 音楽
    lnode = root.add(Category(site=site, hierarchy=u"大", name=u"音楽", label="music", orderno=1, 
                              imgsrc="/static/ticketstar/img/common/header_nav_music.gif"))
    mnode = lnode.add(Category(site=site, hierarchy=u"中", name=u"邦楽", parent=lnode.root))
    snode = mnode.add(Category(site=site, hierarchy=u"小", name=u"ポップス・ロック(邦楽)", parent=mnode.root))

    mnode = lnode.add(Category(site=site, hierarchy=u"中", name=u"洋楽", url="http://example.com"))
    snode = mnode.add(Category(site=site, hierarchy=u"小", name=u"ポップス・ロック(洋楽)", parent=mnode.root))

    ## スポーツ
    lnode = root.add(Category(site=site, hierarchy=u"大", name=u"スポーツ", label="sports", orderno=2, 
                              imgsrc="/static/ticketstar/img/common/header_nav_sports.gif"))
    mnode = lnode.add(Category(site=site, hierarchy=u"中", name=u"野球", parent=lnode.root))
    snode = mnode.add(Category(site=site, hierarchy=u"小", name=u"プロ野球", parent=mnode.root))

    ## 演劇
    lnode = root.add(Category(site=site, hierarchy=u"大", name=u"演劇", label="stage", orderno=3, 
                              imgsrc="/static/ticketstar/img/common/header_nav_stage.gif"))
    mnode = lnode.add(Category(site=site, hierarchy=u"中", name=u"ミュージカル", parent=lnode.root))
    snode = mnode.add(Category(site=site, hierarchy=u"小", name=u"劇団四季", parent=mnode.root))
    
    lnode = root.add(Category(site=site, hierarchy=u"大", name=u"イベント・その他", label="event", orderno=4, 
                              imgsrc="/static/ticketstar/img/common/header_nav_event.gif"))

    ## misc global navigation
    lnode = root.add(Category(site=site, orderno=1, hierarchy=u"top_outer", url="http://example.com", name=u"初めての方へ", label="first"))
    lnode = root.add(Category(site=site, orderno=2, hierarchy=u"top_outer", url="http://example.com", name=u"公演中止・変更情報", label="change"))
    lnode = root.add(Category(site=site, orderno=3, hierarchy=u"top_outer", url="http://example.com", name=u"ヘルプ", label="help"))
    lnode = root.add(Category(site=site, orderno=4, hierarchy=u"top_outer", url="http://example.com", name=u"サイトマップ", label="sitemap"))

    lnode = root.add(Category(site=site, orderno=1, hierarchy=u"top_inner", url="http://example.com", name=u"マイページ", label="mypage"))
    lnode = root.add(Category(site=site, orderno=2, hierarchy=u"top_inner", url="http://example.com", name=u"お気に入り", label="favorite"))
    lnode = root.add(Category(site=site, orderno=3, hierarchy=u"top_inner", url="http://example.com", name=u"購入履歴", label="purchase_history"))
    lnode = root.add(Category(site=site, orderno=4, hierarchy=u"top_inner", url="http://example.com", name=u"抽選申込履歴", label=""))


    root.add_session(DBSession)

def upgrade():
    site, client = _create_materials()
    _create_categories(site)
    import transaction 
    transaction.commit()

def downgrade():
    import transaction
    Category.query.filter_by(hierarchy=u"小").delete()
    transaction.commit()

    Category.query.filter_by(hierarchy=u"中").delete()
    transaction.commit()

    Category.query.delete()
    transaction.commit()

    Site.query.delete()
    transaction.commit()

    Client.query.delete()
    transaction.commit()
