"""create_pgwresponse_log_table

Revision ID: 2e45c8b61b2d
Revises: 5834c84a3af8
Create Date: 2020-03-16 11:27:01.599534

"""

# revision identifiers, used by Alembic.
revision = '2e45c8b61b2d'
down_revision = '5834c84a3af8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('PGWResponseLog',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('payment_id', sa.Unicode(length=50), nullable=False),
                    sa.Column('transaction_time', sa.TIMESTAMP(), nullable=False),
                    sa.Column('transaction_type', sa.Unicode(length=40), nullable=False),
                    sa.Column('transaction_status', sa.Unicode(length=6), nullable=True),
                    sa.Column('pgw_error_code', sa.Unicode(length=50), nullable=True),
                    sa.Column('card_comm_error_code', sa.Unicode(length=6), nullable=True),
                    sa.Column('card_detail_error_code', sa.Unicode(length=512), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    )

def downgrade():
    op.drop_table('PGWResponseLog')
