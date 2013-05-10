"""layout has uploaded_at

Revision ID: 512e091d8fc6
Revises: 29480c8eb277
Create Date: 2013-04-30 18:15:21.367763

"""

# revision identifiers, used by Alembic.
revision = '512e091d8fc6'
down_revision = '29480c8eb277'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('layout', sa.Column('uploaded_at', sa.DateTime(), nullable=True))
    op.add_column('layout', sa.Column('synced_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('layout', 'uploaded_at')
    op.drop_column('layout', 'synced_at')
