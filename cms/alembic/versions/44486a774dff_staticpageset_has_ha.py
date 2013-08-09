"""StaticPageSet has hash

Revision ID: 44486a774dff
Revises: 34639b5a1e44
Create Date: 2013-08-07 11:23:07.150708

"""

# revision identifiers, used by Alembic.
revision = '44486a774dff'
down_revision = '10682b0e9b28'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('static_pagesets', sa.Column('hash', sa.String(length=32), nullable=False))

def downgrade():
    op.drop_column('static_pagesets', 'hash')
