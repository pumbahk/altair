# -*- coding: utf-8 -*-
"""create_famiport_order

Revision ID: 12333853df26
Revises: 33471c50fbc0
Create Date: 2015-04-22 15:45:27.631152

"""

# revision identifiers, used by Alembic.
revision = '12333853df26'
down_revision = '33471c50fbc0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'FamiPortOrder',
        sa.Column('id', Identifier),
        sa.Column('order_no', sa.String(255), nullable=False),  # altair側予約番号
        sa.Column('barcode_no', sa.String(255), nullable=False),  # ファミポート側で使用するバーコード番号 barCodeNo
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        sa.PrimaryKeyConstraint('id'),
        )


def downgrade():
    op.drop_table('FamiPortOrder')
