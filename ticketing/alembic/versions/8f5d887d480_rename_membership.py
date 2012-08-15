"""rename_membership

Revision ID: 8f5d887d480
Revises: f5483384af2
Create Date: 2012-08-10 15:03:47.957426

"""

# revision identifiers, used by Alembic.
revision = '8f5d887d480'
down_revision = 'f5483384af2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.rename_table('MemberShip', 'Membership')

def downgrade():
    op.rename_table('Membership', 'MemberShip')
