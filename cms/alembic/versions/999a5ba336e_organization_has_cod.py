"""organization has code

Revision ID: 999a5ba336e
Revises: 3fec65c2571
Create Date: 2013-03-21 16:51:00.060662

"""

# revision identifiers, used by Alembic.
revision = '999a5ba336e'
down_revision = '3fec65c2571'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('organization', sa.Column('code', sa.String(length=3), nullable=True))

def downgrade():
    op.drop_column('organization', 'code')
