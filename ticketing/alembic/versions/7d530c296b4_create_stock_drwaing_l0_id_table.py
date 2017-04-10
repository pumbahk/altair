"""Create Stock_drwaing_l0_id table

Revision ID: 7d530c296b4
Revises: 17c73ceae5b7
Create Date: 2017-04-07 14:49:35.324493

"""

# revision identifiers, used by Alembic.
revision = '7d530c296b4'
down_revision = '17c73ceae5b7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table(
        'Stock_drawing_l0_id',
        sa.Column('stock_id', Identifier(), primary_key=True),
        sa.Column('drawing_l0_id', sa.Unicode(48), primary_key=True),
    )

def downgrade():
    op.drop_table('Stock_drawing_l0_id')
