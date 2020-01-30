"""add tickethub ticket qr binary column

Revision ID: 56f4aa3cc327
Revises: d06c6c49628
Create Date: 2019-11-29 03:50:10.479134

"""

# revision identifiers, used by Alembic.
revision = '56f4aa3cc327'
down_revision = 'd06c6c49628'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'TicketHubOrderedTicket', sa.Column(u'qr_binary', sa.Binary(), nullable=False))

def downgrade():
    op.drop_column(u'TicketHubOrderedTicket', u'qr_binary')
