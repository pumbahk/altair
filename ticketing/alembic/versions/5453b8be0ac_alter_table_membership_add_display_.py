"""alter table membership add display order and visible

Revision ID: 5453b8be0ac
Revises: 1425b5931a64
Create Date: 2019-06-26 11:23:23.556046

"""

# revision identifiers, used by Alembic.
revision = '5453b8be0ac'
down_revision = '1425b5931a64'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Membership', sa.Column('display_order', sa.Integer(), nullable=False, default=1, server_default='1'))
    op.add_column('Membership', sa.Column('visible', sa.Boolean(), nullable=False, default=True, server_default='1'))


def downgrade():
    op.drop_column('Membership', 'display_order')
    op.drop_column('Membership', 'visible')
