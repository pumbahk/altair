"""add column LotEntry.channel

Revision ID: 49bb9c608cc2
Revises: 53f29cc64fbf
Create Date: 2014-04-16 09:38:49.371108

"""

# revision identifiers, used by Alembic.
revision = '49bb9c608cc2'
down_revision = '53f29cc64fbf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'LotEntry', sa.Column('channel', sa.Integer, nullable=True))

def downgrade():
    op.drop_column(u'LotEntry', 'channel')
