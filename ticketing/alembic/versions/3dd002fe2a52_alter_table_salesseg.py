"""alter table SalesSegment add column

Revision ID: 3dd002fe2a52
Revises: 42a5b8c420d8
Create Date: 2013-03-28 16:39:31.312449

"""

# revision identifiers, used by Alembic.
revision = '3dd002fe2a52'
down_revision = '42a5b8c420d8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'SalesSegment', sa.Column('margin_ratio', sa.Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0'))
    op.add_column(u'SalesSegment', sa.Column('refund_ratio', sa.Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0'))
    op.add_column(u'SalesSegment', sa.Column('printing_fee', sa.Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0'))
    op.add_column(u'SalesSegment', sa.Column('registration_fee', sa.Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0'))

def downgrade():
    op.drop_column(u'SalesSegment', 'registration_fee')
    op.drop_column(u'SalesSegment', 'printing_fee')
    op.drop_column(u'SalesSegment', 'refund_ratio')
    op.drop_column(u'SalesSegment', 'margin_ratio')

