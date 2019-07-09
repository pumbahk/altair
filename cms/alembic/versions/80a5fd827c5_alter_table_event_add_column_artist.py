"""alter table event add column artist

Revision ID: 80a5fd827c5
Revises: 2080f9415bc0
Create Date: 2019-07-08 17:38:48.277207

"""

# revision identifiers, used by Alembic.
revision = '80a5fd827c5'
down_revision = '2080f9415bc0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('event', sa.Column('artist_id', sa.Integer, nullable=True, default=0))
    op.create_foreign_key('fk_event_artist_id_to_artist_id', 'event', 'artist', ['artist_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_event_artist_id_to_artist_id', 'event', type='foreignkey')
    op.drop_column('event', 'artist_id')
