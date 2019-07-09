"""alter table event add column information open date

Revision ID: 38a2950c010f
Revises: 80a5fd827c5
Create Date: 2019-07-08 20:40:51.268161

"""

# revision identifiers, used by Alembic.
revision = '38a2950c010f'
down_revision = '80a5fd827c5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('event', sa.Column('information_open', sa.DateTime(), nullable=True))
    op.add_column('event', sa.Column('information_close', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('event', 'information_close')
    op.drop_column('event', 'information_open')

