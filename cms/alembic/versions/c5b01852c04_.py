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
    op.execute("ALTER TABLE pagesets DROP INDEX url;")
    op.execute("ALTER TABLE pagesets add unique organization_id (organization_id, url);")

def downgrade():
    op.execute("ALTER TABLE pagesets DROP INDEX organization_id;")
    ## don't support it.'
    pass
