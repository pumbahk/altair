"""add orderreview_index

Revision ID: 4fdd3d5caa94
Revises: 1c7b3092c2e3
Create Date: 2016-08-26 16:06:47.012274

"""

# revision identifiers, used by Alembic.
revision = '4fdd3d5caa94'
down_revision = '1c7b3092c2e3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'OrganizationSetting', sa.Column(u'orderreview_index', sa.Integer, nullable=False, default=0, server_default='0'))

def downgrade():
    op.drop_column(u'OrganizationSetting', u'orderreview_index')
