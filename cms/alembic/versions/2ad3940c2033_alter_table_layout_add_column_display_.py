"""alter table layout add column display_order

Revision ID: 2ad3940c2033
Revises: 34ba76bb7cd1
Create Date: 2014-09-26 16:49:13.756367

"""

# revision identifiers, used by Alembic.
revision = '2ad3940c2033'
down_revision = '34ba76bb7cd1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('layout', sa.Column('display_order', sa.Integer(), nullable=False))

def downgrade():
    op.drop_column('layout', 'display_order')
