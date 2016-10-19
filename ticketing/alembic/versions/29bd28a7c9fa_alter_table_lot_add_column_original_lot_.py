"""alter table Lot add column original_lot_id

Revision ID: 29bd28a7c9fa
Revises: 4a99f47c1bd4
Create Date: 2016-09-30 14:52:00.488170

"""

# revision identifiers, used by Alembic.
revision = '29bd28a7c9fa'
down_revision = '4a99f47c1bd4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Lot', sa.Column('original_lot_id', sa.Integer(), nullable=True, default=None))

def downgrade():
    op.drop_column('Lot', 'original_lot_id')
