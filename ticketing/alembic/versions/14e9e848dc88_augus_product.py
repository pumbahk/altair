"""augus_product

Revision ID: 14e9e848dc88
Revises: 4787aa38d83b
Create Date: 2014-02-22 04:48:37.792170

"""

# revision identifiers, used by Alembic.
revision = '14e9e848dc88'
down_revision = '4787aa38d83b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Product', sa.Column('augus_ticket_id', Identifier(), nullable=True))

def downgrade():
    op.drop_column('Product', 'augus_ticket_id')
