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
from altaircms.models import Category
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

def upgrade():   
    root = Node(None)
    ## トップページ
    lnode = root.add(Category(hierarchy=u"大", name=u"チケットトップ", url="http://example.com", label="index", orderno=0, 
                              imgsrc="/static/ticketstar/img/common/header_nav_top.gif"))

    ## 音楽
    lnode = root.add(Category(hierarchy=u"大", name=u"音楽", url="http://example.com", label="music", orderno=1, 
                              imgsrc="/static/ticketstar/img/common/header_nav_music.gif"))
    mnode = lnode.add(Category(hierarchy=u"中", name=u"邦楽", url="http://example.com", parent=lnode.root))
    snode = mnode.add(Category(hierarchy=u"小", name=u"ポップス・ロック(邦楽)", url="http://example.com", parent=mnode.root))

    mnode = lnode.add(Category(hierarchy=u"中", name=u"洋楽", url="http://example.com"))
    snode = mnode.add(Category(hierarchy=u"小", name=u"ポップス・ロック(洋楽)", url="http://example.com", parent=mnode.root))

    ## スポーツ
    lnode = root.add(Category(hierarchy=u"大", name=u"スポーツ", url="http://example.com", label="sports", orderno=2, 
                              imgsrc="/static/ticketstar/img/common/header_nav_sports.gif"))
    mnode = lnode.add(Category(hierarchy=u"中", name=u"野球", url="http://example.com", parent=lnode.root))
    snode = mnode.add(Category(hierarchy=u"小", name=u"プロ野球", url="http://example.com", parent=mnode.root))

    ## 演劇
    lnode = root.add(Category(hierarchy=u"大", name=u"演劇", url="http://example.com", label="theater", orderno=3, 
                              imgsrc="/static/ticketstar/img/common/header_nav_theater.gif"))
    mnode = lnode.add(Category(hierarchy=u"中", name=u"ミュージカル", url="http://example.com", parent=lnode.root))
    snode = mnode.add(Category(hierarchy=u"小", name=u"劇団四季", url="http://example.com", parent=mnode.root))
    
    lnode = root.add(Category(hierarchy=u"大", name=u"イベント・その他", url="http://example.com", label="event", orderno=4, 
                              imgsrc="/static/ticketstar/img/common/header_nav_event.gif"))

    root.add_session(DBSession)

    import transaction 
    transaction.commit()

def downgrade():
    Category.query.delete()
    import transaction
    transaction.commit()

