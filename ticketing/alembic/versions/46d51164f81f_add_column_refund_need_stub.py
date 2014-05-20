"""add column Refund.need_stub

Revision ID: 46d51164f81f
Revises: bc4382b2368
Create Date: 2014-05-20 12:02:28.054080

"""

# revision identifiers, used by Alembic.
revision = '46d51164f81f'
down_revision = 'bc4382b2368'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Refund', sa.Column(u'need_stub', sa.Boolean, nullable=True, default=None))

def downgrade():
    op.drop_column(u'Refund', u'need_stub')
