"""add column ticket.name

Revision ID: 22b3e2ae4c34
Revises: 3adbb1f00111
Create Date: 2012-06-14 11:38:07.933970

"""

# revision identifiers, used by Alembic.
revision = '22b3e2ae4c34'
down_revision = '3adbb1f00111'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('ticket', sa.Column('name', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('ticket', 'name')
