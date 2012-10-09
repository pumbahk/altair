"""order_attribute

Revision ID: 46c057f3d463
Revises: 5585e54d5b5e
Create Date: 2012-09-28 01:54:48.047036

"""

# revision identifiers, used by Alembic.
revision = '46c057f3d463'
down_revision = '597ee3b96465'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('OrderAttribute',
        sa.Column('order_id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=1023), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['Order.id'], name='OrderAttribute_ibfk_1'),
        sa.PrimaryKeyConstraint('order_id', 'name')
    )

def downgrade():
    op.drop_table('OrderAttribute')
