"""add_foreign_key_on_augus_seat

Revision ID: 76aefb1573c
Revises: 4a0f249e86f5
Create Date: 2018-06-19 14:34:12.919530

"""

# revision identifiers, used by Alembic.
revision = '76aefb1573c'
down_revision = '4a0f249e86f5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_foreign_key(
        name='AugusSeat_ibfk_1',
        source='AugusSeat',
        referent='AugusVenue',
        local_cols=['augus_venue_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        name='AugusSeat_ibfk_2',
        source='AugusSeat',
        referent='Seat',
        local_cols=['seat_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('AugusSeat_ibfk_1', 'AugusSeat', type_='foreignkey')
    op.drop_constraint('AugusSeat_ibfk_2', 'AugusSeat', type_='foreignkey')
