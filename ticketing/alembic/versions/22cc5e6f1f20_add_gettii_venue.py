"""add_gettii_venue

Revision ID: 22cc5e6f1f20
Revises: 3c93bddaec70
Create Date: 2014-03-07 13:46:46.955678

"""

# revision identifiers, used by Alembic.
revision = '22cc5e6f1f20'
down_revision = '3c93bddaec70'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'GettiiVenue',
        sa.Column('id', Identifier, primary_key=True),
        )
    op.create_table(
        'GettiiSeat',
        sa.Column('id', Identifier, primary_key=True),
        )

def downgrade():
    op.drop_table('GettiiVenue')
    op.drop_table('GettiiSeat')
