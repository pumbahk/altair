"""alter table Order drop column stopped_at and add column cancel_reason

Revision ID: 1f92f73d0a7e
Revises: 6289f2d8cbf
Create Date: 2013-01-15 18:16:43.874106

"""

# revision identifiers, used by Alembic.
revision = '1f92f73d0a7e'
down_revision = '6289f2d8cbf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('Order', 'stopped_at')
    op.add_column('Order', sa.Column('cancel_reason', sa.String(length=32), nullable=True, default=None))

def downgrade():
    op.drop_column('Order', 'cancel_reason')
    op.add_column('Order', sa.Column('stopped_at', sa.DateTime(), nullable=True, default=None))
