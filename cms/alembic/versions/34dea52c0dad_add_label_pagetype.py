"""add label pagetype

Revision ID: 34dea52c0dad
Revises: 220b8dc5b1be
Create Date: 2013-02-22 13:57:27.819941

"""

# revision identifiers, used by Alembic.
revision = '34dea52c0dad'
down_revision = '220b8dc5b1be'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('pagetype', sa.Column('label', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('pagetype', 'label')
