"""#tkt1188 add enable_random_import to OrderImportTask

Revision ID: 39b1645c028e
Revises: ddaa27c32b6
Create Date: 2016-03-09 18:04:18.591181

"""

# revision identifiers, used by Alembic.
revision = '39b1645c028e'
down_revision = 'ddaa27c32b6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrderImportTask', sa.Column('enable_random_import', sa.Boolean(), nullable=False, default=False, server_default='0'))

def downgrade():
    op.drop_column('OrderImportTask', 'enable_random_import')
