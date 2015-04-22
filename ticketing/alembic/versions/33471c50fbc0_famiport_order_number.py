# -*- coding: utf-8 -*-
"""famiport_order_number

Revision ID: 33471c50fbc0
Revises: c35141f8f11
Create Date: 2015-04-22 15:03:39.513828

"""

# revision identifiers, used by Alembic.
revision = '33471c50fbc0'
down_revision = 'c35141f8f11'


from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'FamiPortOrderNoSequence',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        )


def downgrade():
    op.drop_table('FamiPortOrderNoSequence')
