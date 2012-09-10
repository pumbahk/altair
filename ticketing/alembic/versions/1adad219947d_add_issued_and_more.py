"""add_issued_and_more

Revision ID: 1adad219947d
Revises: 557f1172f037
Create Date: 2012-09-07 10:16:36.994665

"""

# revision identifiers, used by Alembic.
revision = '1adad219947d'
down_revision = '557f1172f037'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Order', sa.Column('issued', sa.Boolean, default=False, server_default=text('0')))
    op.add_column('Order', sa.Column('last_issued_at', sa.TIMESTAMP(), default=None, nullable=True))

def downgrade():
    op.drop_column('Order', 'issued')
    op.drop_column('Order', 'last_issued_at')
