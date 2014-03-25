"""augus_venue_sync_response_batch

Revision ID: 330fbffaf765
Revises: 4a89e94a84d9
Create Date: 2014-03-25 12:55:44.718639

"""

# revision identifiers, used by Alembic.
revision = '330fbffaf765'
down_revision = '4a89e94a84d9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'AugusVenue', sa.Column('reserved_at', sa.DateTime, nullable=True, default=None))
    op.add_column(u'AugusVenue', sa.Column('notified_at', sa.DateTime, nullable=True, default=None))

def downgrade():
    op.drop_column(u'AugusVenue', 'reserved_at')
    op.drop_column(u'AugusVenue', 'notified_at')
