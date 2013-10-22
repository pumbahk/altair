"""add organization.use_only_one_static_page_type

Revision ID: 3edabd243c83
Revises: 346832ed83a8
Create Date: 2013-10-22 16:34:01.052670

"""

# revision identifiers, used by Alembic.
revision = '3edabd243c83'
down_revision = '346832ed83a8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('organization', sa.Column('use_only_one_static_page_type', sa.Boolean(), server_default="1", nullable=False))
    op.execute('UPDATE organization set use_only_one_static_page_type = 0 where short_name="eagles"')

def downgrade():
    op.drop_column('organization', 'use_only_one_static_page_type')
