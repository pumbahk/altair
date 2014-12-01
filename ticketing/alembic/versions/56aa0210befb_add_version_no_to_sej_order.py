"""add_version_no_to_sej_order

Revision ID: 56aa0210befb
Revises: 5a9a795b4aa8
Create Date: 2014-12-01 19:26:59.752233

"""

# revision identifiers, used by Alembic.
revision = '56aa0210befb'
down_revision = '5a9a795b4aa8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SejOrder', sa.Column('version_no', sa.Integer, nullable=False, default=0))
    op.drop_constraint('ix_SejOrder_order_no_branch_no', 'SejOrder', type_='unique')
    op.create_unique_constraint('ix_SejOrder_order_version_no_branch_no', 'SejOrder', ['order_no', 'version_no', 'branch_no'])

def downgrade():
    op.drop_constraint('ix_SejOrder_order_no_branch_no', 'SejOrder', type_='unique')
    op.drop_column('SejOrder', 'version_no')
    op.create_unique_constraint('ix_SejOrder_order_no_branch_no', 'SejOrder', ['order_no', 'branch_no'])
