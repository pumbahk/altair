"""#tkt1110 add visible to TicketFormat

Revision ID: 1fd783a5bb9
Revises: 42c129c74985
Create Date: 2016-02-23 16:58:27.652184

"""

# revision identifiers, used by Alembic.
revision = '1fd783a5bb9'
down_revision = '42c129c74985'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('TicketFormat', sa.Column('visible', sa.Boolean(), nullable=False, default=True, server_default='1'))

def downgrade():
    op.drop_column('TicketFormat', 'visible')
