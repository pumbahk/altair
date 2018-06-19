"""add_foreign_key_on_augus_venue

Revision ID: 1451c64d8a4c
Revises: 3edeff1e01e0
Create Date: 2018-06-19 14:32:55.703241

"""

# revision identifiers, used by Alembic.
revision = '1451c64d8a4c'
down_revision = '3edeff1e01e0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_foreign_key(
        name='AugusVenue_ibfk_1',
        source='AugusVenue',
        referent='AugusAccount',
        local_cols=['augus_account_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        name='AugusVenue_ibfk_2',
        source='AugusVenue',
        referent='Venue',
        local_cols=['venue_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('AugusVenue_ibfk_1', 'AugusVenue', type_='foreignkey')
    op.drop_constraint('AugusVenue_ibfk_2', 'AugusVenue', type_='foreignkey')
