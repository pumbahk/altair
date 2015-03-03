"""Create unique index on page_accesskeys.hashkey

Revision ID: 4a5e16404a86
Revises: c09a614defd
Create Date: 2015-03-02 13:22:13.510557

"""

# revision identifiers, used by Alembic.
revision = '4a5e16404a86'
down_revision = 'c09a614defd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint("unq_page_accesskeys_hashkey", "page_accesskeys", ["hashkey"])

def downgrade():
    op.drop_constraint("unq_page_accesskeys_hashkey", "page_accesskeys", type="unique")
