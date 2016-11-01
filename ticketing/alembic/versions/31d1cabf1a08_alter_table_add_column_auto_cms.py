"""alter table add column auto_cms

Revision ID: 31d1cabf1a08
Revises: 29bd28a7c9fa
Create Date: 2016-10-26 15:18:08.708117

"""

# revision identifiers, used by Alembic.
revision = '31d1cabf1a08'
down_revision = '29bd28a7c9fa'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('auto_cms', sa.Boolean(), nullable=False,default=False, server_default=text('0')))

def downgrade():
    op.drop_column('OrganizationSetting', 'auto_cms')
