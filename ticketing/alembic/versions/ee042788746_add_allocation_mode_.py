"""add_allocation_mode_to_order_import_task

Revision ID: ee042788746
Revises: 1b061c1f4490
Create Date: 2014-02-06 20:47:12.117670

"""

# revision identifiers, used by Alembic.
revision = 'ee042788746'
down_revision = '1b061c1f4490'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrderImportTask', sa.Column('allocation_mode', sa.Integer(), default=1, server_default=text('1'), nullable=False))

def downgrade():
    op.drop_column('OrderImportTask', 'allocation_mode')
