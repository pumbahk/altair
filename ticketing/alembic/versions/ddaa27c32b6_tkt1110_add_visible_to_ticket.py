"""#tkt1110 add visible to Ticket

Revision ID: ddaa27c32b6
Revises: 1fd783a5bb9
Create Date: 2016-02-24 10:17:23.429799

"""

# revision identifiers, used by Alembic.
revision = 'ddaa27c32b6'
down_revision = '1fd783a5bb9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Ticket', sa.Column('visible', sa.Boolean(), nullable=False, default=True, server_default='1'))

def downgrade():
    op.drop_column('Ticket', 'visible')
