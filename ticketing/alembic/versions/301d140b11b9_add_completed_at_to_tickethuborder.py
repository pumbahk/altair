"""add completed_at to TicketHubOrder

Revision ID: 301d140b11b9
Revises: 56f4aa3cc327
Create Date: 2019-12-10 09:08:08.383470

"""

# revision identifiers, used by Alembic.
revision = '301d140b11b9'
down_revision = '56f4aa3cc327'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('TicketHubOrder', sa.Column('completed_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('TicketHubOrder', 'completed_at')
