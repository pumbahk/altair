"""#tkt479 add lot_entry_user_withdraw to Lot

Revision ID: 566dd0ea18db
Revises: 313b31142eb7
Create Date: 2015-12-01 09:29:18.551316

"""

# revision identifiers, used by Alembic.
revision = '566dd0ea18db'
down_revision = '313b31142eb7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Lot', sa.Column('lot_entry_user_withdraw', sa.Boolean(), nullable=False, default=False, server_default='0'))

def downgrade():
    op.drop_column('Lot', 'lot_entry_user_withdraw')
