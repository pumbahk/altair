"""alter table Order add column stopped_at

Revision ID: 6289f2d8cbf
Revises: 4ce21170ef11
Create Date: 2012-12-25 15:43:13.270822

"""

# revision identifiers, used by Alembic.
revision = '6289f2d8cbf'
down_revision = '4ce21170ef11'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Order', sa.Column('stopped_at', sa.DateTime(), nullable=True, default=None))
    op.add_column('Order', sa.Column('refunded_at', sa.DateTime(), nullable=True, default=None))
    op.execute("UPDATE `Order` SET refunded_at = canceled_at WHERE canceled_at IS NOT NULL AND paid_at IS NOT NULL")

def downgrade():
    op.drop_column('Order', 'stopped_at')
    op.drop_column('Order', 'refunded_at')
