"""empty message

Revision ID: 2257df21db29
Revises: 3381e7b8fb9b
Create Date: 2015-01-19 15:34:18.246356

"""

# revision identifiers, used by Alembic.
revision = '2257df21db29'
down_revision = '3381e7b8fb9b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('promotion', sa.Column('trackingcode', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('promotion', 'trackingcode')
