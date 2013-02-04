"""empty message

Revision ID: c5b01852c04
Revises: 435502b9fa0c
Create Date: 2012-07-30 17:37:07.415030

"""

# revision identifiers, used by Alembic.
revision = 'c5b01852c04'
down_revision = '435502b9fa0c'

from alembic import op
import sqlalchemy as sa


def upgrade(): 
    op.drop_index("url", "pagesets")
    op.create_unique_constraint("organization_id", "pagesets", ["organization_id", "url"])

def downgrade():
    op.drop_index("organization_id", "pagesets")
    op.create_unique_constraint("url", "pagesets", ["url"])
