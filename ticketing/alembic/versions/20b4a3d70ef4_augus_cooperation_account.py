"""augus_cooperation_account

Revision ID: 20b4a3d70ef4
Revises: 45e17ff9f21a
Create Date: 2014-07-22 11:24:19.464676

"""

# revision identifiers, used by Alembic.
revision = '20b4a3d70ef4'
down_revision = '45e17ff9f21a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

MAX_LENGTH = 0xFF
def upgrade():
    op.create_table(
        'AugusAccount',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('account_id', Identifier(), nullable=False),
        sa.Column('code', sa.Integer, nullable=False),
        sa.Column('name', sa.Unicode(MAX_LENGTH), nullable=False),
        sa.Column('host', sa.Unicode(MAX_LENGTH), nullable=False),
        sa.Column('username', sa.Unicode(MAX_LENGTH), nullable=False),
        sa.Column('password', sa.Unicode(MAX_LENGTH), nullable=False),
        sa.Column('send_dir', sa.Unicode(MAX_LENGTH), nullable=False),
        sa.Column('recv_dir', sa.Unicode(MAX_LENGTH), nullable=False),
        )
    op.add_column(
        'AugusVenue',
        sa.Column('augus_account_id', Identifier(), nullable=True),
        )
    op.add_column(
        'AugusTicket',
        sa.Column('augus_account_id', Identifier(), nullable=True),
        )
    op.add_column(
        'AugusPerformance',
        sa.Column('augus_account_id', Identifier(), nullable=True),
        )
    op.add_column(
        'AugusStockInfo',
        sa.Column('augus_account_id', Identifier(), nullable=True),
        )
    op.add_column(
        'AugusPutback',
        sa.Column('augus_account_id', Identifier(), nullable=True),
        )
def downgrade():
    op.drop_table('AugusAccount')
    op.drop_column('AugusVenue', 'augus_account_id')
    op.drop_column('AugusTicket', 'augus_account_id')
    op.drop_column('AugusPerformance', 'augus_account_id')
    op.drop_column('AugusStockInfo', 'augus_account_id')
    op.drop_column('AugusPutback', 'augus_account_id')
