"""add column backend_id

Revision ID: 1faa6cd3ba1
Revises: 3ed842f1b24c
Create Date: 2012-06-18 14:25:09.751840

"""

# revision identifiers, used by Alembic.
revision = '1faa6cd3ba1'
down_revision = '3ed842f1b24c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('sale', sa.Column('backend_id', sa.Integer))
    op.add_column('ticket', sa.Column('backend_id', sa.Integer))

def downgrade():
    op.drop_column('sale', 'backend_id')
    op.drop_column('ticket', 'backend_id')
