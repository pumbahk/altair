"""empty message

Revision ID: 3381e7b8fb9b
Revises: 5040333dbb9c
Create Date: 2014-12-26 16:14:08.467795

"""

# revision identifiers, used by Alembic.
revision = '3381e7b8fb9b'
down_revision = '5040333dbb9c'

from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    op.create_table('featuresetting',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('organization_id', sa.Integer, sa.ForeignKey('Organization.id')),
        sa.Column('name', sa.String(length=255)),
        sa.Column('value', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(),  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(),  server_default=sa.text('now()'), server_onupdate=sa.text('now()')),
        sa.UniqueConstraint('organization_id', 'name'))

def downgrade():
    op.drop_table('featuresetting')
