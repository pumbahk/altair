# -*- coding:utf-8 -*-
"""insert category master

Revision ID: b5ecfbf167f
Revises: 137096ec0baa
Create Date: 2012-05-09 16:11:36.812424

"""

# revision identifiers, used by Alembic.
revision = 'b5ecfbf167f'
down_revision = '137096ec0baa'

from alembic import op
import sqlalchemy as sa

import sqlahelper
from altaircms.models import Category
DBSession = sqlahelper.get_session()

def upgrade():
    ## 音楽
    lnode = Category(hierarchy=u"大", name=u"音楽", url="http://example.com")
    mnode = Category(hierarchy=u"中", name=u"邦楽", url="http://example.com", parent=lnode)
    snode = Category(hierarchy=u"小", name=u"ポップス・ロック(邦楽)", url="http://example.com", parent=mnode)
    mnode = Category(hierarchy=u"中", name=u"洋楽", url="http://example.com", parent=lnode)
    snode = Category(hierarchy=u"小", name=u"ポップス・ロック(洋楽)", url="http://example.com", parent=mnode)
    DBSession.add(lnode)
    
    ## スポーツ
    lnode = Category(hierarchy=u"大", name=u"スポーツ", url="http://example.com")
    mnode = Category(hierarchy=u"中", name=u"野球", url="http://example.com", parent=lnode)
    snode = Category(hierarchy=u"小", name=u"プロ野球", url="http://example.com", parent=mnode)
    DBSession.add(lnode)

    import transaction 
    transaction.commit()

def downgrade():
    Category.query.delete()
    import transaction
    transaction.commit()
