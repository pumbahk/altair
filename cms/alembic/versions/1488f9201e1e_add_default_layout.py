"""add default layout settings

Revision ID: 1488f9201e1e
Revises: 34dea52c0dad
Create Date: 2013-02-25 09:45:02.838038

"""

# revision identifiers, used by Alembic.
revision = '1488f9201e1e'
down_revision = '34dea52c0dad'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('layout', sa.Column('disposition_id', sa.Integer(), nullable=True)) #default settings
    op.add_column('widgetdisposition', sa.Column('layout_id', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('layout', 'disposition_id')
    op.drop_column('widgetdisposition', 'layout_id')
