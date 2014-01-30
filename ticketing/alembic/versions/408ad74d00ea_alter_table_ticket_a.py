"""alter table Ticket add column cover_print

Revision ID: 408ad74d00ea
Revises: 29ec8e3c3462
Create Date: 2014-01-29 20:15:59.619147

"""

# revision identifiers, used by Alembic.
revision = '408ad74d00ea'
down_revision = '29ec8e3c3462'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Ticket', sa.Column('cover_print', sa.Boolean(), nullable=False,default=True, server_default=text('1')))

def downgrade():
    op.drop_column('Ticket', 'cover_print')

