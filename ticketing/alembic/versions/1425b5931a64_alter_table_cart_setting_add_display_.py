"""alter table cart setting add display order and visible

Revision ID: 1425b5931a64
Revises: 3a31f6169bd1
Create Date: 2019-06-13 17:36:58.812543

"""

# revision identifiers, used by Alembic.
revision = '1425b5931a64'
down_revision = '3a31f6169bd1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('CartSetting', sa.Column('display_order', sa.Integer(), nullable=False, default=1, server_default='1'))
    op.add_column('CartSetting', sa.Column('visible', sa.Boolean(), nullable=False, default=True, server_default='1'))

def downgrade():
    op.drop_column('CartSetting', 'display_order')
    op.drop_column('CartSetting', 'visible')
