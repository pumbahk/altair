"""add columns to DeliveryMethod

Revision ID: 4ab26bf2ebf2
Revises: 3269e5ab0f4e
Create Date: 2015-06-19 10:34:45.000022

"""

# revision identifiers, used by Alembic.
revision = '4ab26bf2ebf2'
down_revision = '496e1d9bba37'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('DeliveryMethod', sa.Column('display_order', sa.Integer(), default=0, nullable=False))
    op.add_column('DeliveryMethod', sa.Column('selectable', sa.Boolean(), default=True, nullable=False))
    op.execute(u"update DeliveryMethod set selectable=True;")

def downgrade():
    op.drop_column('DeliveryMethod', 'display_order')
    op.drop_column('DeliveryMethod', 'selectable')
