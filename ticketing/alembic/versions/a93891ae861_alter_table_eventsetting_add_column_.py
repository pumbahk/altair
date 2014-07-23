"""alter table EventSetting add column middle_stock_threshold, middle_stock_threshold_percent

Revision ID: a93891ae861
Revises: 975937d8dec
Create Date: 2014-07-20 16:30:18.943245

"""

# revision identifiers, used by Alembic.
revision = 'a93891ae861'
down_revision = '975937d8dec'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('EventSetting', sa.Column('middle_stock_threshold', sa.Integer(), nullable=True))
    op.add_column('EventSetting', sa.Column('middle_stock_threshold_percent', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('EventSetting', 'middle_stock_threshold')
    op.drop_column('EventSetting', 'middle_stock_threshold_percent')
