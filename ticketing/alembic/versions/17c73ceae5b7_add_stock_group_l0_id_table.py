"""add Stock_group_l0_id table

Revision ID: 17c73ceae5b7
Revises: 1f9dae4d0c08
Create Date: 2017-03-29 10:27:18.459498

"""

# revision identifiers, used by Alembic.
revision = '17c73ceae5b7'
down_revision = '1f9dae4d0c08'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('Stock_group_l0_id',
        sa.Column('stock_id', Identifier(), primary_key=True),
        sa.Column('group_l0_id', sa.Unicode(48), primary_key=True),
    )

def downgrade():
    op.drop_table('Stock_group_l0_id')
