# -*- coding: utf-8 -*-
"""add orion delivery method

Revision ID: 177e7846ed2b
Revises: 43c53ca49806
Create Date: 2014-01-23 10:09:05.469634

"""

# revision identifiers, used by Alembic.
revision = '177e7846ed2b'
down_revision = '43c53ca49806'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute(u"INSERT INTO DeliveryMethodPlugin (id, name) VALUES(5, 'イベント・ゲート')")

def downgrade():
    op.execute(u"DELETE FROM DeliveryMethodPlugin WHERE id=5")

