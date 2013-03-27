"""alter table Organization add columns

Revision ID: 19d54c1f7e06
Revises: 17984d0ecfd2
Create Date: 2013-03-26 16:10:50.114898

"""

# revision identifiers, used by Alembic.
revision = '19d54c1f7e06'
down_revision = '17984d0ecfd2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Organization', sa.Column('margin_ratio', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Organization', sa.Column('refund_ratio', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Organization', sa.Column('printing_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Organization', sa.Column('registration_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'SalesSegmentGroup', sa.Column('margin_ratio', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'SalesSegmentGroup', sa.Column('refund_ratio', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'SalesSegmentGroup', sa.Column('printing_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'SalesSegmentGroup', sa.Column('registration_fee', sa.Numeric(precision=16, scale=2), nullable=False))

def downgrade():
    op.drop_column(u'SalesSegmentGroup', 'registration_fee')
    op.drop_column(u'SalesSegmentGroup', 'printing_fee')
    op.drop_column(u'SalesSegmentGroup', 'refund_ratio')
    op.drop_column(u'SalesSegmentGroup', 'margin_ratio')
    op.drop_column(u'Organization', 'registration_fee')
    op.drop_column(u'Organization', 'printing_fee')
    op.drop_column(u'Organization', 'refund_ratio')
    op.drop_column(u'Organization', 'margin_ratio')

