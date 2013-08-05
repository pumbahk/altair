"""add_public_in_payment_method

Revision ID: 2bb9f0027253
Revises: 304ea58e981
Create Date: 2013-08-05 10:43:03.470098

"""

# revision identifiers, used by Alembic.
revision = '2bb9f0027253'
down_revision = '304ea58e981'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('PaymentMethod', sa.Column('public', sa.Boolean(), nullable=False, default=True, server_default=text('1')))

def downgrade():
    op.drop_column('PaymentMethod', 'public')
