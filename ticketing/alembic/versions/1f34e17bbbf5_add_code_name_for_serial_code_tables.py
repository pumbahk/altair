"""add code name for serial code tables

Revision ID: 1f34e17bbbf5
Revises: 1abac4199f5a
Create Date: 2019-10-25 10:41:58.247292

"""

# revision identifiers, used by Alembic.
revision = '1f34e17bbbf5'
down_revision = '1abac4199f5a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('''ALTER TABLE ExternalSerialCode ADD code_1_name varchar(255) AFTER external_serial_code_setting_id;''')
    op.execute('''ALTER TABLE ExternalSerialCode ADD code_2_name varchar(255) AFTER code_1;''')


def downgrade():
    op.drop_column('ExternalSerialCode', 'code_1_name')
    op.drop_column('ExternalSerialCode', 'code_2_name')

