# -*- coding:utf-8 -*-
"""cart_item_name

Revision ID: 2e752dabe105
Revises: 3426fcec916a
Create Date: 2013-03-27 18:02:27.514016

"""

# revision identifiers, used by Alembic.
revision = '2e752dabe105'
down_revision = '3426fcec916a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute(u"UPDATE OrganizationSetting SET cart_item_name = '楽天チケット'")

def downgrade():
    pass
