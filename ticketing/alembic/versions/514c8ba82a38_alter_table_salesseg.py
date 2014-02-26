"""alter table SalesSegment, SalesSegmentGroup add column disp_orderreview

Revision ID: 514c8ba82a38
Revises: 533d3473a1f3
Create Date: 2014-02-21 19:34:23.209228

"""

# revision identifiers, used by Alembic.
revision = '514c8ba82a38'
down_revision = '533d3473a1f3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegment', sa.Column('disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
    op.add_column('SalesSegment', sa.Column('use_default_disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
    op.add_column('SalesSegmentGroup', sa.Column('disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))

def downgrade():
    op.drop_column('SalesSegment', 'disp_orderreview')
    op.drop_column('SalesSegment', 'use_default_disp_orderreview')
    op.drop_column('SalesSegmentGroup', 'disp_orderreview')
