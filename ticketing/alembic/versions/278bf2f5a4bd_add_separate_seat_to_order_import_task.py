"""add_separate_seat_to_order_import_task

Revision ID: 278bf2f5a4bd
Revises: 29fa4108127c
Create Date: 2014-04-24 13:47:36.878306

"""

# revision identifiers, used by Alembic.
revision = '278bf2f5a4bd'
down_revision = '29fa4108127c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrderImportTask', sa.Column('entrust_separate_seats', sa.Boolean, default=False, nullable=False))

def downgrade():
    op.drop_column('OrderImportTask', 'entrust_separate_seats')
