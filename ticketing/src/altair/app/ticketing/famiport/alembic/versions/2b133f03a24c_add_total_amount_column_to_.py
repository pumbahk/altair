"""Add total_amount column to FamiPortRefundEntry.

Revision ID: 2b133f03a24c
Revises: 3c9de6a251b5
Create Date: 2018-12-03 14:11:40.806740

"""

# revision identifiers, used by Alembic.
revision = '2b133f03a24c'
down_revision = '3c9de6a251b5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('FamiPortRefundEntry', sa.Column('total_amount', sa.Numeric(precision=16, scale=0), nullable=False))
    op.execute('UPDATE FamiPortRefundEntry SET total_amount = ticket_payment + ticketing_fee + other_fees;')

def downgrade():
    op.drop_column('FamiPortRefundEntry', 'total_amount')
