"""alter table event add column in_preparation

Revision ID: 45124fe5e11a
Revises: 346832ed83a8
Create Date: 2013-10-23 16:05:26.916296

"""

# revision identifiers, used by Alembic.
revision = '45124fe5e11a'
down_revision = '346832ed83a8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('event', sa.Column('in_preparation', sa.Boolean(), nullable=False))

def downgrade():
    op.drop_column('event', 'in_preparation')
