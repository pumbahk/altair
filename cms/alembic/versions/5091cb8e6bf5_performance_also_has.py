"""performance also has display_order.

Revision ID: 5091cb8e6bf5
Revises: 151de63d5dd4
Create Date: 2013-04-12 12:15:35.291488

"""

# revision identifiers, used by Alembic.
revision = '5091cb8e6bf5'
down_revision = '151de63d5dd4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('performance', sa.Column('display_order', sa.Integer(), nullable=True, default=50))
    op.execute("update performance set display_order = 50;")

def downgrade():
    op.drop_column('performance', 'display_order')
