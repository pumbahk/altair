"""alter table Stock add column locked_at

Revision ID: 14a36b46cfa7
Revises: 3dd002fe2a52
Create Date: 2013-04-02 10:11:25.478151

"""

# revision identifiers, used by Alembic.
revision = '14a36b46cfa7'
down_revision = '3dd002fe2a52'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Stock', sa.Column('locked_at', sa.DateTime, nullable=True, default=None))

def downgrade():
    op.drop_column(u'Stock', 'locked_at')

