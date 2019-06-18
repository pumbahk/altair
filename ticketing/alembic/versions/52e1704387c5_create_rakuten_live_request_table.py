"""create rakuten live request table

Revision ID: 52e1704387c5
Revises: 14814b6b5f89
Create Date: 2019-06-14 13:22:08.739010

"""

# revision identifiers, used by Alembic.
revision = '52e1704387c5'
down_revision = '14814b6b5f89'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'RakutenLiveRequest',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('order_entry_no', sa.Unicode(255), index=True),
        sa.Column('live_user_id', sa.Integer()),
        sa.Column('live_stream_id', sa.Integer()),
        sa.Column('live_channel_id', sa.Integer()),
        sa.Column('live_slug', sa.Unicode(255)),
        sa.Column('live_product_id', sa.Integer()),
        sa.Column('status', sa.SmallInteger(), default=0),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False, index=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP()),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('RakutenLiveRequest')
