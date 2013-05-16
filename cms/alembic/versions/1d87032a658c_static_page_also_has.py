"""static page also has pageset

Revision ID: 1d87032a658c
Revises: 512e091d8fc6
Create Date: 2013-05-17 00:11:37.496714

"""

# revision identifiers, used by Alembic.
revision = '1d87032a658c'
down_revision = '512e091d8fc6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('static_pages', sa.Column('pageset_id', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('static_pages', 'pageset_id')
