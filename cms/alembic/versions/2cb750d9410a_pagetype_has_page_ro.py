"""pagetype has page role field

Revision ID: 2cb750d9410a
Revises: 26fdc4343dc0
Create Date: 2013-02-27 19:48:50.067934

"""

# revision identifiers, used by Alembic.
revision = '2cb750d9410a'
down_revision = '26fdc4343dc0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('pagetype', sa.Column('page_role', sa.String(length=16), nullable=True))
    op.add_column('pagetype', sa.Column('page_rendering_type', sa.String(length=16), nullable=True))

def downgrade():
    op.drop_column('pagetype', 'page_role')
    op.drop_column('pagetype', 'page_rendering_type')

