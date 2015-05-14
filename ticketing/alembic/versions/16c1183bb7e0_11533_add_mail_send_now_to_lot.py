"""#11533 add mail_send_now to Lot

Revision ID: 16c1183bb7e0
Revises: cd9211f5a5b
Create Date: 2015-04-30 18:04:32.408367

"""

# revision identifiers, used by Alembic.
revision = '16c1183bb7e0'
down_revision = 'cd9211f5a5b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Lot', sa.Column('mail_send_now', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('Lot', 'mail_send_now')
