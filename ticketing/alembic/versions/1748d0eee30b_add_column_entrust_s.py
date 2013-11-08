"""add column entrust_separate_seats

Revision ID: 1748d0eee30b
Revises: f58218c5f54
Create Date: 2013-11-08 15:03:40.557253

"""

# revision identifiers, used by Alembic.
revision = '1748d0eee30b'
down_revision = 'f58218c5f54'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('entrust_separate_seats', sa.Boolean(), nullable=False, default=False, server_default=text('0')))
    op.execute("UPDATE OrganizationSetting SET entrust_separate_seats = '1' WHERE organization_id = 23")

def downgrade():
    op.drop_column('OrganizationSetting', 'entrust_separate_seats')
