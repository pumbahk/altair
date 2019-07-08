"""alter table artist add column display_order

Revision ID: 2080f9415bc0
Revises: 4ef27985730b
Create Date: 2019-07-03 14:32:18.321425

"""

# revision identifiers, used by Alembic.
revision = '2080f9415bc0'
down_revision = '4ef27985730b'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('artist', sa.Column('display_order', sa.Integer(), nullable=False))

    op.create_table('provider',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('provider_type', sa.Unicode(length=255), nullable=False),
                    sa.Column('service_id', sa.Unicode(length=255), nullable=False),
                    sa.Column('service_id', sa.Unicode(length=255), nullable=False),
                    sa.Column('artist_id', sa.Integer, nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], name="fk_provider_artist_id_to_artist_id"))


def downgrade():
    op.drop_table('provider')
    op.drop_column('artist', 'display_order')
