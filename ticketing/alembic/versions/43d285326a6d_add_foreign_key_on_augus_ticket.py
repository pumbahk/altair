"""add_foreign_key_on_augus_ticket

Revision ID: 43d285326a6d
Revises: 133bd4ddc44a
Create Date: 2018-06-19 14:33:50.654553

"""

# revision identifiers, used by Alembic.
revision = '43d285326a6d'
down_revision = '133bd4ddc44a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_foreign_key(
        name='AugusTicket_ibfk_1',
        source='AugusTicket',
        referent='AugusPerformance',
        local_cols=['augus_performance_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        name='AugusTicket_ibfk_2',
        source='AugusTicket',
        referent='AugusAccount',
        local_cols=['augus_account_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('AugusTicket_ibfk_1', 'AugusTicket', type_='foreignkey')
    op.drop_constraint('AugusTicket_ibfk_2', 'AugusTicket', type_='foreignkey')
