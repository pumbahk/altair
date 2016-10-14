"""add enable search column

Revision ID: 4d76c7847d67
Revises: 236c1c6e7dad
Create Date: 2016-10-13 16:05:10.706741

"""

# revision identifiers, used by Alembic.
revision = '4d76c7847d67'
down_revision = '236c1c6e7dad'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'organization', sa.Column("enable_search", sa.Boolean(), server_default=('1')))

def downgrade():
    op.drop_column(u'organization', "enable_search")
