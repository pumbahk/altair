"""alter table Refund add column

Revision ID: 27aa0c829578
Revises: 3ee99f3f1e61
Create Date: 2013-02-25 13:52:27.015265

"""

# revision identifiers, used by Alembic.
revision = '27aa0c829578'
down_revision = '3ee99f3f1e61'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Refund', sa.Column('include_system_fee', sa.Boolean, nullable=False, default=False))
    op.add_column('Refund', sa.Column('include_transaction_fee', sa.Boolean, nullable=False, default=False))
    op.add_column('Refund', sa.Column('include_delivery_fee', sa.Boolean, nullable=False, default=False))
    op.execute("update Refund set include_system_fee = include_fee, include_transaction_fee = include_fee, include_delivery_fee = include_fee")
    op.drop_column('Refund', 'include_fee')

def downgrade():
    op.add_column('Refund', sa.Column('include_fee', sa.Boolean, nullable=False, default=False))
    op.execute("update Refund set include_fee = include_system_fee")
    op.drop_column('Refund', 'include_delivery_fee')
    op.drop_column('Refund', 'include_transaction_fee')
    op.drop_column('Refund', 'include_system_fee')
