"""empty message

Revision ID: 500167ad61bd
Revises: 580e3305babf
Create Date: 2015-01-20 10:00:41.535509

"""

# revision identifiers, used by Alembic.
revision = '500167ad61bd'
down_revision = '580e3305babf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('topcontent', sa.Column('trackingcode', sa.String(255), nullable=True))

def downgrade():
    op.drop_column('topcontent', 'trackingcode')
