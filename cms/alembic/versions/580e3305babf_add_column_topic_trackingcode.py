"""empty message

Revision ID: 580e3305babf
Revises: 2257df21db29
Create Date: 2015-01-19 15:38:18.567915

"""

# revision identifiers, used by Alembic.
revision = '580e3305babf'
down_revision = '2257df21db29'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('topic', sa.Column('trackingcode', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('topic', 'trackingcode')
