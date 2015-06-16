"""ticketing table PaymentMethod add columns

Revision ID: 3269e5ab0f4e
Revises: 569b8783f4f9
Create Date: 2015-06-12 16:22:51.626130

"""

# revision identifiers, used by Alembic.
revision = '3269e5ab0f4e'
down_revision = '569b8783f4f9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('PaymentMethod', sa.Column('display_order', sa.Integer(), default=0, nullable=False))
    op.add_column('PaymentMethod', sa.Column('selectable', sa.Boolean(), default=True, nullable=False))

def downgrade():
    op.drop_column('PaymentMethod', 'display_order')
    op.drop_column('PaymentMethod', 'selectable')
