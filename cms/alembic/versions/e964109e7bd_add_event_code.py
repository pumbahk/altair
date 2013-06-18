"""add event code

Revision ID: e964109e7bd
Revises: 1488f9201e1e
Create Date: 2013-02-26 15:34:32.311163

"""

# revision identifiers, used by Alembic.
revision = 'e964109e7bd'
down_revision = '1488f9201e1e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('event', sa.Column('code', sa.String(length=12), nullable=True))

def downgrade():
    op.drop_column('event', 'code')

