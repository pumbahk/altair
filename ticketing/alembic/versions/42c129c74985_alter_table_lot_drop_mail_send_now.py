"""alter table Lot drop mail_send_now

Revision ID: 42c129c74985
Revises: 9538f560df2
Create Date: 2016-02-19 17:50:41.185308

"""

# revision identifiers, used by Alembic.
revision = '42c129c74985'
down_revision = '9538f560df2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('Lot', 'mail_send_now')

def downgrade():
    op.add_column('Lot', sa.Column('mail_send_now', sa.Boolean(), nullable=False, server_default='0'))
