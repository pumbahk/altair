"""add_foreign_key_on_augus_putback

Revision ID: 133bd4ddc44a
Revises: 3bb9b6990f58
Create Date: 2018-06-19 14:33:43.162429

"""

# revision identifiers, used by Alembic.
revision = '133bd4ddc44a'
down_revision = '3bb9b6990f58'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_foreign_key(
        name='AugusPutback_ibfk_1',
        source='AugusPutback',
        referent='AugusPerformance',
        local_cols=['augus_performance_id'],
        remote_cols=['id']
    )

    op.create_foreign_key(
        name='AugusPutback_ibfk_2',
        source='AugusPutback',
        referent='AugusAccount',
        local_cols=['augus_account_id'],
        remote_cols=['id']
    )


def downgrade():
    op.drop_constraint('AugusPutback_ibfk_1', 'AugusPutback', type_='foreignkey')
    op.drop_constraint('AugusPutback_ibfk_2', 'AugusPutback', type_='foreignkey')
    op.drop_index('AugusPutback_ibfk_1', 'AugusPutback')
    op.drop_index('AugusPutback_ibfk_2', 'AugusPutback')
